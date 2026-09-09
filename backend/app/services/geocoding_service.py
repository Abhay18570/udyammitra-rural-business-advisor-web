from fastapi import HTTPException

from app.engines.nearby_market_engine import fingerprint, location_fingerprint, normalize_location
from app.providers.errors import ProviderError
from app.repositories.nearby_market_repository import utcnow

LOCALITY_KEYS = ("village", "town", "city", "suburb", "hamlet", "municipality")


def acceptable_candidate(candidate, location):
    address = candidate["address"]
    if address.get("country_code", "").lower() != "in":
        return "REJECTED"
    if normalize_location(address.get("state")) != normalize_location(location["state"]):
        return "REJECTED"
    districts = [normalize_location(address.get(key)) for key in ("district", "county", "state_district") if address.get(key)]
    if districts and normalize_location(location["district"]) not in districts:
        return "REJECTED"
    locality_match = any(normalize_location(address.get(key)) == normalize_location(location["village"]) for key in LOCALITY_KEYS)
    if locality_match and districts and candidate["precision"] in LOCALITY_KEYS:
        return "RESOLVED"
    return "AMBIGUOUS"


class GeocodingService:
    def __init__(self, repository, provider, settings):
        self.repository, self.provider, self.settings = repository, provider, settings

    def resolve(self, location, deadline):
        fp = location_fingerprint(location)
        key = fingerprint({"location": fp, "provider": str(self.settings.nominatim_base_url), "version": "geocoding-v1"})
        cached = self.repository.geocode(key)
        if cached and cached["expires_at"] > utcnow():
            return self._read(cached, fp)
        lease = self.repository.acquire("geocode-query-" + key, deadline)
        try:
            # Recheck after acquiring the refresh lease.
            cached = self.repository.geocode(key)
            if cached and cached["expires_at"] > utcnow():
                return self._read(cached, fp)
            queries = list(dict.fromkeys([
                ", ".join(location[field].strip() for field in ("village", "taluka", "district", "state")) + ", India",
                ", ".join(location[field].strip() for field in ("village", "district", "state")) + ", India",
            ]))
            ambiguous = []
            for query in queries:
                provider_lease = self.repository.acquire("nominatim", deadline, min_interval=self.settings.geocoding_min_interval_seconds,
                                                         wait_seconds=self.settings.geocoding_min_interval_seconds + 0.2)
                cooldown = None
                try:
                    candidates = self.provider.search(query, deadline)
                except ProviderError as exc:
                    cooldown = exc.retry_after
                    raise
                finally:
                    self.repository.release(provider_lease, cooldown or self.settings.geocoding_min_interval_seconds)
                accepted, possible = [], []
                for candidate in candidates:
                    status = acceptable_candidate(candidate, location)
                    if status == "RESOLVED":
                        accepted.append(candidate)
                    if status != "REJECTED":
                        possible.append(candidate)
                # Multiple locality candidates must never be resolved by provider ordering.
                unique = {(c["latitude"], c["longitude"]): c for c in possible}
                if len(accepted) == 1 and len(unique) == 1:
                    cached = self.repository.save_geocode(key, fp, "RESOLVED", {"location": accepted[0]}, self.settings.geocoding_cache_ttl_seconds)
                    return self._read(cached, fp)
                ambiguous.extend(unique.values())
                if len(unique) > 1:
                    break
            status = "AMBIGUOUS" if ambiguous else "NO_MATCH"
            cached = self.repository.save_geocode(key, fp, status, {"candidates": ambiguous[:5]}, self.settings.geocoding_negative_cache_ttl_seconds)
            return self._read(cached, fp)
        finally:
            self.repository.release(lease)

    @staticmethod
    def _read(cached, fp):
        if cached["status"] == "NO_MATCH":
            raise HTTPException(status_code=422, detail={"code": "LOCATION_NOT_RESOLVED", "message": "Your locality could not be resolved. Check the village, taluka, district and state in your profile."})
        if cached["status"] == "AMBIGUOUS":
            raise HTTPException(status_code=409, detail={"code": "LOCATION_CONFIRMATION_REQUIRED", "message": "The location is ambiguous or too coarse. Correct your profile locality before searching; candidate confirmation is not available yet.",
                                                       "candidates": cached["result"]["candidates"]})
        return {**cached["result"]["location"], "location_fingerprint": fp, "fetched_at": cached["fetched_at"], "expires_at": cached["expires_at"]}
