import logging
import time
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.business_query_rules import classify_query, VERSION

from app.core.config import get_settings
from app.osm_business_rules import BUSINESS_RULES
from app.providers.errors import ProviderError
from app.providers.geocoding import NominatimProvider
from app.providers.nearby import ProviderPolicy
from app.providers.http import remaining, DeadlineClient
from app.repositories.business_repository import BusinessRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.nearby_market_repository import NearbyMarketRepository, utcnow
from app.schemas.nearby_market import NearbyMarketResponse
from app.services.geocoding_service import GeocodingService

logger = logging.getLogger(__name__)



class NearbyMarketService:
    def __init__(self, db, settings=None, geocoder=None, overpass=None, client=None):
        self.db = db
        self.settings = settings or get_settings()
        self.repository = NearbyMarketRepository(db)
        self.policy = ProviderPolicy(self.settings)
        self.geocoder, self.overpass, self.client = geocoder, overpass, client

    def analyze(self, user, payload):
        radius_meters = payload.radius_km * 1000
        started = time.monotonic()
        deadline = started + self.settings.nearby_request_timeout_seconds
        repository = BusinessRepository(self.db)
        business = repository.get_active(payload.business_slug) if payload.business_slug else None
        if payload.business_slug and not business:
            raise HTTPException(status_code=404, detail="Active business profile not found.")
        if payload.business_query:
            # Only literal catalog name/slug matches may establish a relationship.
            matches = [b for b in repository.list_active() if payload.business_query.casefold() in {b.name.casefold(), b.slug.casefold()}]
            exact = matches[0] if matches else None
            if business and (not exact or business.id != exact.id):
                raise HTTPException(status_code=422, detail={'code': 'BUSINESS_QUERY_MISMATCH'})
            business = exact
        if not self.policy.google and (not business or business.slug not in BUSINESS_RULES):
            raise HTTPException(status_code=422, detail={"code": "OVERPASS_CATALOG_REQUIRED"})
        context = {"id": business.id if business else None, "slug": business.slug if business else None,
                   "display_name": payload.business_query or business.name}
        query = payload.business_query or business.name
        profile = ProfileRepository(self.db).get_for_user(user)
        if not profile or not all(getattr(profile, field) and getattr(profile, field).strip() for field in ("village", "taluka", "district", "state")):
            raise HTTPException(status_code=409, detail={"code": "PROFILE_LOCATION_REQUIRED", "message": "Complete village, taluka, district and state in your profile before finding nearby businesses."})
        location_fields = {field: getattr(profile, field) for field in ("village", "taluka", "district", "state", "pincode")}
        # Capture only locality fields; profile coordinates have no verified provenance.
        owns_client = self.client is None
        client = self.client or DeadlineClient()
        try:
            location = GeocodingService(self.repository, self.geocoder or NominatimProvider(self.settings, client), self.settings).resolve(location_fields, deadline)
            if self.policy.google:
                return self._google_response(context, query, location, deadline, client, payload.radius_km, bool(payload.business_query))
            key = self.policy.cache_key(context["slug"], location, radius_meters)
            cache = self.repository.query_cache(key)
            source = "FRESH_CACHE"
            stale_warning = None
            if not cache or not cache["complete"] or cache["expires_at"] <= utcnow():
                try:
                    refresh_lease = self.repository.acquire("nearby-query-" + key, deadline)
                    try:
                        cache_after_lock = self.repository.query_cache(key)
                        if cache_after_lock and cache_after_lock["complete"] and cache_after_lock["expires_at"] > utcnow():
                            cache = cache_after_lock
                        else:
                            provider_lease = self.repository.acquire(self.policy.name, deadline, slots=1 if self.policy.google else self.settings.overpass_max_concurrent_requests)
                            cooldown = None
                            try:
                                pois, rejected = (self.overpass if not self.policy.google and self.overpass else self.policy.provider(client)).fetch(context["slug"], location["latitude"], location["longitude"], deadline, radius_meters)
                                if rejected:
                                    raise ProviderError("PROVIDER_PARTIAL_RESPONSE")
                            except ProviderError as exc:
                                cooldown = exc.retry_after
                                raise
                            finally:
                                self.repository.release(provider_lease, cooldown)
                            remaining(deadline)
                            ttl = self.settings.nearby_cache_ttl_seconds if pois else self.settings.nearby_empty_cache_ttl_seconds
                            cache = self.repository.save_query(key, location, context["slug"], self.policy.mapping_version, pois, ttl, radius_meters, provider=self.policy.storage_provider)
                            source = "FRESH_FETCH"
                    finally:
                        self.repository.release(refresh_lease)
                except ProviderError as exc:
                    if not cache or not cache["complete"] or (utcnow() - cache["fetched_at"]).total_seconds() > self.settings.nearby_stale_max_age_seconds:
                        raise
                    source = "STALE_CACHE"
                    stale_warning = {"code": "STALE_CACHE", "message": "The provider could not refresh this search. Showing older cached evidence with its original observation date."}
                    logger.warning("Nearby provider fallback code=%s", exc.code)
            result = self._response(context, location, cache, source, stale_warning, payload.radius_km)
            logger.info("Nearby evidence completed source=%s duration_ms=%d", source, int((time.monotonic() - started) * 1000))
            return result
        except ProviderError as exc:
            logger.warning("Nearby provider failure code=%s", exc.code)
            raise HTTPException(status_code=exc.status, detail={"code": exc.code, "message": "The geographic data provider is temporarily unavailable or busy. Please retry later."},
                                headers={"Retry-After": str(exc.retry_after)} if exc.retry_after else None) from exc
        finally:
            if owns_client:
                client.close()

    def _google_response(self, business, query, location, deadline, client, radius_km, text_search):
        # Google content is request-local, including legacy catalog requests.
        key = self.policy.text_request_key(query, location, radius_km * 1000) if text_search else self.policy.cache_key(business['slug'], location, radius_km * 1000)
        lease = self.repository.acquire('google-query-' + key, deadline)
        try:
            provider_lease = self.repository.acquire('google', deadline)
            cooldown = None
            try:
                provider = self.policy.provider(client)
                pois, rejected = (provider.fetch_text(query, location['latitude'], location['longitude'], deadline, radius_km * 1000)
                                  if text_search else provider.fetch(business['slug'], location['latitude'], location['longitude'], deadline, radius_km * 1000))
                if rejected:
                    raise ProviderError('PROVIDER_PARTIAL_RESPONSE')
            except ProviderError as exc:
                cooldown = exc.retry_after
                raise
            finally:
                self.repository.release(provider_lease, cooldown)
            try:
                spatial = self.repository.spatial_candidates(pois, location, radius_km * 1000)
            except SQLAlchemyError:
                self.db.rollback()
                raise ProviderError('SPATIAL_QUERY_FAILED', 503) from None
            now = utcnow()
            cache = {'complete': True, 'rejected_record_count': 0, 'fetched_at': now, 'expires_at': now,
                     'mapping_version': VERSION if text_search else self.policy.mapping_version}
            return self._response(business, location, cache, 'FRESH_FETCH', None, radius_km,
                                  spatial=spatial, query=query, text_search=text_search)
        finally:
            self.repository.release(lease)

    def _response(self, business, location, cache, source, stale_warning, radius_km, spatial=None, query=None, text_search=False):
        direct, related, generic = [], [], []
        for poi in spatial if spatial is not None else self.repository.spatial_pois(cache["poi_ids"], location, radius_km * 1000):
            match = classify_query(query, poi["name"], poi["normalized_tags"], business["slug"] or "") if text_search else self.policy.match(business["slug"], poi["normalized_tags"])
            if not match:
                continue
            # Geographic display rounding is separate from authoritative band classification.
            km = (Decimal(str(poi["distance_meters"])) / Decimal("1000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            record = {**poi, **match, "distance_km": format(km, ".2f")}
            {"DIRECT_COMPETITOR": direct, "RELATED_BUSINESS": related, "GENERIC_POI": generic}[match["classification"]].append(record)
        warnings = ([{'code': 'GOOGLE_RANKED_SUBSET', 'message': 'Google Places returns available/ranked search results and may not include every establishment in the selected area.'}]
                    if text_search else self.policy.warnings(business["slug"]))
        if not direct:
            warnings.append({"code": "NO_MAPPED_DIRECT_COMPETITORS", "message": "No mapped direct competitors were found in the available Google Places data." if self.policy.google else "No mapped direct competitors were found in the available OpenStreetMap data."})
        if stale_warning:
            warnings.append(stale_warning)
        return NearbyMarketResponse.model_validate({"business": business, "business_query": query or business["display_name"], "matched_catalog_business_slug": business["slug"], "location": location,
            "radius": {"selected_km": radius_km, "selected_meters": radius_km * 1000},
            "summary": {"direct_competitors": len(direct), "related_businesses": len(related), "nearest_direct_competitor": direct[0] if direct else None},
            "competitors": direct, "related_businesses": related, "generic_pois": generic,
            "source": {"provider": self.policy.source_provider, "mode": "LIVE" if source == "FRESH_FETCH" else "CACHE", "cache_status": source,
                       "fetched_at": cache["fetched_at"], "expires_at": cache["expires_at"], "mapping_version": cache["mapping_version"]},
            "quality": {"complete_query": cache["complete"], "rejected_record_count": cache["rejected_record_count"], "warnings": warnings, "attribution": self.policy.attribution}})
