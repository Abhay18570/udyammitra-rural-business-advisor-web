import time
import uuid
from datetime import datetime, timedelta, timezone

from geoalchemy2 import Geometry
from sqlalchemy import Float, Integer, column, values as sql_values, BigInteger, case, cast, func, select, update
from sqlalchemy.dialects.postgresql import insert

from app.models.market_cache import GeocodingCache, NearbyQueryCache, ProviderRequestState
from app.models.market_poi import MarketPOI
from app.providers.errors import ProviderError
from app.providers.http import remaining
from app.utils.spatial import geography_point, distance_meters, within_meters


def utcnow():
    return datetime.now(timezone.utc)


class NearbyMarketRepository:
    def __init__(self, db):
        self.db = db

    def geocode(self, key):
        row = self.db.get(GeocodingCache, key, populate_existing=True)
        if row is None:
            return None
        return {field: getattr(row, field) for field in ("status", "result", "fetched_at", "expires_at")}

    def save_geocode(self, key, location_fp, status, result, ttl):
        now = utcnow()
        values = dict(key=key, location_fingerprint=location_fp, status=status, result=result, fetched_at=now, expires_at=now + timedelta(seconds=ttl))
        statement = insert(GeocodingCache).values(**values)
        self.db.execute(statement.on_conflict_do_update(index_elements=[GeocodingCache.key], set_=values))
        self.db.commit()
        return values

    def query_cache(self, key):
        row = self.db.get(NearbyQueryCache, key, populate_existing=True)
        if row is None:
            return None
        return {field: getattr(row, field) for field in ("key", "poi_ids", "complete", "rejected_record_count", "fetched_at", "expires_at", "mapping_version")}

    def save_query(self, key, location, slug, mapping_version, pois, ttl, radius_meters=10000, provider="OPENSTREETMAP"):
        if provider == 'GOOGLE_PLACES' or any(p['provider'] == 'GOOGLE_PLACES' for p in pois):
            raise ValueError('Google display content must remain transient')
        now, ids = utcnow(), []
        try:
            for poi in pois:
                values = {key: poi[key] for key in ("provider", "external_type", "name", "coordinate_kind", "normalized_tags", "normalized_address")}
                values.update(external_id=str(poi["external_id"]), fetched_at=now,
                              geo_point=geography_point(poi["latitude"], poi["longitude"]))
                statement = insert(MarketPOI).values(id=uuid.uuid4(), **values)
                ids.append(self.db.scalar(statement.on_conflict_do_update(constraint="uq_market_poi_external", set_=values).returning(MarketPOI.id)))
            values = dict(key=key, latitude=location["latitude"], longitude=location["longitude"], radius_meters=radius_meters,
                          provider=provider, business_slug=slug, mapping_version=mapping_version, poi_ids=ids,
                          complete=True, rejected_record_count=0, fetched_at=now, expires_at=now + timedelta(seconds=ttl))
            statement = insert(NearbyQueryCache).values(**values)
            self.db.execute(statement.on_conflict_do_update(index_elements=[NearbyQueryCache.key], set_=values))
            self.db.commit()
            return values
        except Exception:
            self.db.rollback()
            raise

    def spatial_pois(self, ids, location, radius_meters=10000):
        if not ids:
            return []
        origin = geography_point(location["latitude"], location["longitude"])
        distance = distance_meters(MarketPOI.geo_point, origin)
        geometry = cast(MarketPOI.geo_point, Geometry(geometry_type="POINT", srid=4326))
        # Slightly wider indexed candidates avoid ST_DWithin boundary disagreement.
        # The unrounded ST_Distance predicate below remains authoritative.
        query = select(MarketPOI, distance, func.ST_Y(geometry), func.ST_X(geometry)).where(
            MarketPOI.id.in_(ids), within_meters(MarketPOI.geo_point, origin, radius_meters + 0.001), distance <= radius_meters).order_by(
                distance, MarketPOI.provider, MarketPOI.external_type,
                case((MarketPOI.provider == "OPENSTREETMAP", cast(MarketPOI.external_id, BigInteger)), else_=None),
                MarketPOI.external_id)
        results = []
        for row, meters, latitude, longitude in self.db.execute(query):
            results.append({"provider": row.provider, "external_type": row.external_type, "external_id": str(row.external_id),
                            "name": row.name, "latitude": latitude, "longitude": longitude,
                            "coordinate_kind": row.coordinate_kind, "normalized_tags": row.normalized_tags,
                            "normalized_address": row.normalized_address, "fetched_at": row.fetched_at,
                            "distance_meters": meters})
        return results

    def spatial_candidates(self, pois, location, radius_meters):
        """Request-local VALUES relation; identical spheroidal predicates, no inserts."""
        if not pois:
            return []
        candidates = sql_values(column('idx', Integer), column('lat', Float), column('lon', Float),
                                name='candidates').data([(i, p['latitude'], p['longitude']) for i, p in enumerate(pois)])
        origin = geography_point(location['latitude'], location['longitude'])
        point = geography_point(candidates.c.lat, candidates.c.lon)
        distance = distance_meters(point, origin)
        query = select(candidates.c.idx, distance).where(
            within_meters(point, origin, radius_meters + 0.001), distance <= radius_meters).order_by(distance, candidates.c.idx)
        now = utcnow()
        return [{**pois[i], 'distance_meters': meters, 'fetched_at': now} for i, meters in self.db.execute(query)]

    def acquire(self, group, deadline, *, slots=1, min_interval=0, wait_seconds=0):
        """Short transactions reserve expiring slots; no row lock spans network I/O."""
        owner = uuid.uuid4()
        stop_waiting = time.monotonic() + wait_seconds
        while True:
            now = utcnow()
            for slot in range(slots):
                key = f"{group}:{slot}"
                self.db.execute(insert(ProviderRequestState).values(key=key, next_allowed_at=now, lease_until=now).on_conflict_do_nothing())
                acquired = self.db.scalar(update(ProviderRequestState).where(
                    ProviderRequestState.key == key, ProviderRequestState.next_allowed_at <= func.clock_timestamp(),
                    ProviderRequestState.lease_until <= func.clock_timestamp()).values(
                        lease_owner=owner, lease_until=now + timedelta(seconds=remaining(deadline) + 5),
                        next_allowed_at=now + timedelta(seconds=min_interval)).returning(ProviderRequestState.key))
                self.db.commit()
                if acquired:
                    return key, owner
            if time.monotonic() >= stop_waiting:
                raise ProviderError("PROVIDER_RATE_LIMITED", 429, 2)
            time.sleep(min(0.1, remaining(deadline)))

    def release(self, lease, cooldown=None):
        key, owner = lease
        values = {"lease_until": utcnow(), "lease_owner": None}
        self.db.execute(update(ProviderRequestState).where(ProviderRequestState.key == key, ProviderRequestState.lease_owner == owner).values(**values))
        if cooldown:
            group = key.rsplit(":", 1)[0]
            self.db.execute(update(ProviderRequestState).where(ProviderRequestState.key.like(group + ":%")).values(
                next_allowed_at=func.greatest(ProviderRequestState.next_allowed_at, utcnow() + timedelta(seconds=cooldown))))
        self.db.commit()
