import math
from typing import Protocol

from app.providers.errors import ProviderError
from app.providers.http import request_json


class GeocodingProvider(Protocol):
    def search(self, query: str, deadline: float) -> list: ...


class NominatimProvider:
    def __init__(self, settings, client):
        self.settings, self.client = settings, client

    def search(self, query, deadline):
        raw = request_json(self.client, "GET", str(self.settings.nominatim_base_url).rstrip("/") + "/search",
                           deadline=deadline, timeout=self.settings.geocoding_timeout_seconds, max_bytes=262144,
                           params={"q": query, "format": "jsonv2", "countrycodes": "in", "addressdetails": 1, "limit": 5},
                           headers={"User-Agent": self.settings.osm_user_agent, "Accept-Language": "en"})
        if not isinstance(raw, list) or len(raw) > 5:
            raise ProviderError("PROVIDER_INVALID_RESPONSE")
        candidates = []
        for item in raw:
            try:
                if isinstance(item["lat"], bool) or isinstance(item["lon"], bool):
                    raise ValueError()
                lat, lon = float(item["lat"]), float(item["lon"])
                if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
                    raise ValueError()
                address = item["address"]
                if not isinstance(address, dict) or not isinstance(item["display_name"], str):
                    raise ValueError()
                candidates.append({"latitude": lat, "longitude": lon, "display_name": item["display_name"][:1000],
                    "address": {k: str(v)[:200] for k, v in address.items() if k in {"country_code", "state", "state_district", "county", "district", "village", "town", "city", "suburb", "hamlet", "municipality", "postcode"}},
                    "precision": str(item.get("addresstype", item.get("type", "unknown")))[:80], "provider": "NOMINATIM", "query_used": query})
            except (KeyError, TypeError, ValueError, OverflowError) as exc:
                raise ProviderError("PROVIDER_INVALID_RESPONSE") from exc
        return candidates
