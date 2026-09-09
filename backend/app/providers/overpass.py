import json
import math

from app.osm_business_rules import BUSINESS_RULES
from app.providers.errors import ProviderError
from app.providers.http import request_json


def build_query(slug, latitude, longitude, timeout, radius_meters=10000):
    if type(radius_meters) is not int or not 1000 <= radius_meters <= 10000:
        raise ValueError("Invalid radius")
    envelope = radius_meters + 100  # Candidate buffer; PostGIS enforces the selected radius.
    rules = BUSINESS_RULES.get(slug)
    if not rules:
        raise ValueError("Unsupported business mapping")
    if not math.isfinite(latitude) or not math.isfinite(longitude) or not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("Invalid coordinates")
    # Exact token regex handles semicolon-separated OSM values; literals are backend-owned.
    clauses = []
    for rule in rules:
        filters = "".join(f'[{json.dumps(key)}~{json.dumps("(^|;) *" + value + " *(;|$)")}]' for key, value in rule.tags)
        clauses.append(f"nwr(around:{envelope},{latitude:.7f},{longitude:.7f}){filters};")
    return f"[out:json][timeout:{int(timeout)}];(" + "".join(clauses) + ");out center tags;"


def normalize_elements(raw, max_elements):
    if not isinstance(raw, dict) or raw.get("remark") or not isinstance(raw.get("elements"), list):
        raise ProviderError("PROVIDER_INVALID_RESPONSE")
    if len(raw["elements"]) > max_elements:
        raise ProviderError("PROVIDER_TOO_MANY_ELEMENTS")
    pois, seen, rejected = [], set(), 0
    for element in raw["elements"]:
        try:
            kind, external_id = element["type"], element["id"]
            if kind not in {"node", "way", "relation"} or type(external_id) is not int or not 0 < external_id <= 9223372036854775807:
                raise ValueError()
            coordinate = element if kind == "node" else element["center"]
            if isinstance(coordinate["lat"], bool) or isinstance(coordinate["lon"], bool):
                raise ValueError()
            lat, lon = float(coordinate["lat"]), float(coordinate["lon"])
            if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
                raise ValueError()
            tags = element.get("tags", {})
            if not isinstance(tags, dict) or len(tags) > 200 or any(not isinstance(k, str) or not isinstance(v, str) or len(k) > 200 or len(v) > 2000 for k, v in tags.items()):
                raise ValueError()
            key = (kind, external_id)
            if key in seen:
                continue
            seen.add(key)
            allowed = {"name", "shop", "craft", "electronics_repair", "mobile_phone:repair", "landuse", "produce", "industrial", "butcher", "man_made", "product", "agrarian", "rental", "disused", "abandoned", "demolished", "construction"}
            normalized = {k: v for k, v in tags.items() if k in allowed or k.startswith(("disused:", "abandoned:", "demolished:", "construction:", "was:"))}
            address = {k[5:]: v for k, v in tags.items() if k in {"addr:street", "addr:housenumber", "addr:city", "addr:postcode", "addr:suburb", "addr:village"}}
            pois.append({"provider": "OPENSTREETMAP", "external_type": kind, "external_id": str(external_id),
                         "name": tags.get("name") or "Unnamed mapped business", "latitude": lat, "longitude": lon,
                         "coordinate_kind": "NODE" if kind == "node" else "REPRESENTATIVE_CENTER",
                         "normalized_tags": normalized, "normalized_address": address})
        except (TypeError, KeyError, ValueError, OverflowError):
            rejected += 1
    if rejected and not pois:
        raise ProviderError("PROVIDER_INVALID_RESPONSE")
    return pois, rejected


class OverpassProvider:
    def __init__(self, settings, client):
        self.settings, self.client = settings, client

    def fetch(self, slug, latitude, longitude, deadline, radius_meters=10000):
        query = build_query(slug, latitude, longitude, self.settings.overpass_query_timeout_seconds, radius_meters)
        raw = request_json(self.client, "POST", str(self.settings.overpass_base_url), deadline=deadline,
                           timeout=self.settings.overpass_timeout_seconds, max_bytes=self.settings.overpass_max_response_bytes,
                           data={"data": query}, headers={"User-Agent": self.settings.osm_user_agent})
        return normalize_elements(raw, self.settings.overpass_max_elements)
