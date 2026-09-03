import re
import uuid
from collections import Counter
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.market_config import DEMO_MARKET_DATA_VERSION, MARKET_ANALYSIS_VERSION, clamp_score, competition_scores, score_label
from app.models.market import AmenityType, DemoAmenity, DemoInstitution, DemoLocalBusiness, MarketAnalysis
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.repositories.market_repository import MarketRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.market import MarketAnalysisRequest, MarketAnalysisResponse, MarketLocation, MarketLocationsResponse

DISCLAIMER = "This prototype uses curated demonstration market data to illustrate hyper-local feasibility analysis. It should not be treated as a complete live census of businesses or consumer demand."
ACCESS_WEIGHTS = {AmenityType.MARKET: 20, AmenityType.MAJOR_ROAD: 25, AmenityType.BUS_STAND: 15, AmenityType.TRANSPORT_NODE: 20, AmenityType.BANK: 10, AmenityType.AGRI_MARKET: 10}
DISTRIBUTION_TYPES = {AmenityType.MARKET, AmenityType.BUS_STAND, AmenityType.MAJOR_ROAD, AmenityType.WAREHOUSE, AmenityType.COLD_STORAGE, AmenityType.TRANSPORT_NODE, AmenityType.AGRI_MARKET, AmenityType.COLLECTION_CENTRE}


def normalize_location(value):
    return re.sub(r"[^a-z0-9]", "", (value or "").casefold())


class MarketService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.market = MarketRepository(db)
        self.profiles = ProfileRepository(db)
        self.businesses = BusinessRepository(db)

    def _profile(self, user):
        profile = self.profiles.get_for_user(user)
        if not profile:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Complete your entrepreneur profile before running market analysis.")
        return profile

    def _resolve(self, profile):
        required = (profile.village, profile.taluka, profile.district, profile.state)
        if not all(required):
            return None
        target = tuple(normalize_location(value) for value in required)
        for location in self.market.list_locations():
            candidate = tuple(normalize_location(value) for value in (location.village, location.taluka, location.district, location.state))
            if candidate == target:
                return location
        return None

    def locations(self, user: User) -> MarketLocationsResponse:
        resolved = self._resolve(self._profile(user))
        return MarketLocationsResponse(locations=[MarketLocation.model_validate(item) for item in self.market.list_locations()], resolved_location_slug=resolved.slug if resolved else None, resolution_status="resolved_demo_location" if resolved else "unsupported_demo_location", data_version=DEMO_MARKET_DATA_VERSION, disclaimer=DISCLAIMER)

    def run(self, user: User, payload: MarketAnalysisRequest) -> MarketAnalysisResponse:
        if payload.radius_km not in (5, 10):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Analysis radius must be 5 km or 10 km.")
        profile = self._profile(user)
        resolved = self._resolve(profile)
        location_source = "profile"
        if payload.demo_location_slug:
            location = self.market.get_location(payload.demo_location_slug)
            location_source = "demo_override"
            if not location:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supported demonstration location not found.")
        else:
            location = resolved
            if not location:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Profile location is outside current demonstration coverage. Select a demo analysis location.")
        result = self._calculate(location, payload.radius_km)
        profile_snapshot = {"state": profile.state, "district": profile.district, "taluka": profile.taluka, "village": profile.village, "pincode": profile.pincode, "latitude": str(profile.latitude) if profile.latitude is not None else None, "longitude": str(profile.longitude) if profile.longitude is not None else None}
        snapshot = {**result, "location_source": location_source}
        analysis = self.market.save_analysis(MarketAnalysis(user_id=user.id, demo_location_id=location.id, profile_location_snapshot=profile_snapshot, analysis_radius_km=payload.radius_km, analysis_version=MARKET_ANALYSIS_VERSION, data_version=DEMO_MARKET_DATA_VERSION, result_snapshot=snapshot))
        return self._response(analysis)

    def latest(self, user: User) -> MarketAnalysisResponse:
        analysis = self.market.latest(user.id)
        if not analysis:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No saved market analysis found.")
        return self._response(analysis)

    def get(self, user: User, analysis_id: uuid.UUID) -> MarketAnalysisResponse:
        analysis = self.market.get_owned(analysis_id, user.id)
        if not analysis:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market analysis not found.")
        return self._response(analysis)

    @staticmethod
    def _response(analysis):
        return MarketAnalysisResponse.model_validate({"id": analysis.id, "created_at": analysis.created_at, "analysis_version": analysis.analysis_version, "data_version": analysis.data_version, **analysis.result_snapshot})

    def _calculate(self, location, radius):
        institutions = self.market.nearby(DemoInstitution, location, radius)
        amenities = self.market.nearby(DemoAmenity, location, radius)
        local_businesses = self.market.nearby(DemoLocalBusiness, location, radius)
        institution_counts = Counter(item.institution_type.value for item, _ in institutions)
        amenity_distances = [(item, float(distance)) for item, distance in amenities]
        reach = clamp_score(location.settlement_density_signal * .45 + location.commercial_activity_signal * .25 + min(len(institutions) * 4, 20) + min(len(amenities) * 3, 15) + (5 if radius == 10 else 0))
        access = self._market_access(amenity_distances)
        channels = [{"type": item.amenity_type.value, "name": item.name, "distance_km": round(distance, 2)} for item, distance in amenity_distances if item.amenity_type in DISTRIBUTION_TYPES]
        results = []
        for business in self.businesses.list_active():
            competitors = [(item, float(distance)) for item, distance in self.market.matching_businesses(location, business.id)]
            rings = [sum(1 for _, distance in competitors if distance <= 2), sum(1 for _, distance in competitors if 2 < distance <= 5), sum(1 for _, distance in competitors if 5 < distance <= 10)]
            nearest = competitors[0][1] if competitors else None
            competition, competition_opportunity = competition_scores(*rings, nearest)
            demand = self._demand(business.slug, location, reach, access, institution_counts, {item.amenity_type.value for item, _ in amenities}, competition)
            supply = self._supply_chain(business.slug, location.agriculture_intensity_signal, access, {item.amenity_type for item, _ in amenities})
            threats = self._threats(business.slug, competition, access, supply, {item.amenity_type for item, _ in amenities})
            selected_count = sum(1 for _, distance in competitors if distance <= radius)
            evidence = ["{} institution points within {} km".format(len(institutions), radius), "{} amenity/access points within {} km".format(len(amenities), radius), "{} matching demonstration competitors within {} km".format(selected_count, radius), "Settlement activity signal: {}/100".format(location.settlement_density_signal), "Commercial activity signal: {}/100".format(location.commercial_activity_signal), "Agriculture intensity signal: {}/100".format(location.agriculture_intensity_signal)]
            results.append({"business_id": str(business.id), "business_slug": business.slug, "business_name": business.name, "business_category": business.category.value, "competitors_0_2_km": rings[0], "competitors_2_5_km": rings[1], "competitors_5_10_km": rings[2], "competitors_within_2_km": rings[0], "competitors_within_5_km": rings[0] + rings[1], "competitors_within_10_km": sum(rings), "competitors_within_selected_radius": selected_count, "nearest_competitor_km": round(nearest, 2) if nearest is not None else None, "competition_intensity": competition, "competition_label": score_label(competition), "competition_opportunity_score": competition_opportunity, "demand_score": demand, "demand_label": score_label(demand), "market_reach_score": reach, "market_access_score": access, "supply_chain_score": supply, "distribution_channels": channels, "localized_threats": threats, "evidence": evidence, "nearby_competitors": [{"name": item.name, "category": item.category.value, "distance_km": round(distance, 2)} for item, distance in competitors], "market_opportunity_signal": clamp_score((competition_opportunity + demand + reach) / 3)})
        lower = [item["business_name"] for item in sorted(results, key=lambda row: row["competition_intensity"])[:3]]
        higher = [item["business_name"] for item in sorted(results, key=lambda row: row["demand_score"], reverse=True)[:3]]
        strong_access = [item["business_name"] for item in sorted(results, key=lambda row: row["market_access_score"], reverse=True)[:3]]
        map_points = [{"kind": "BUSINESS", "name": item.name, "subtype": item.category.value, "latitude": float(item.latitude), "longitude": float(item.longitude), "distance_km": round(float(distance), 2)} for item, distance in local_businesses]
        map_points += [{"kind": "INSTITUTION", "name": item.name, "subtype": item.institution_type.value, "latitude": float(item.latitude), "longitude": float(item.longitude), "distance_km": round(float(distance), 2)} for item, distance in institutions]
        map_points += [{"kind": "AMENITY", "name": item.name, "subtype": item.amenity_type.value, "latitude": float(item.latitude), "longitude": float(item.longitude), "distance_km": round(float(distance), 2)} for item, distance in amenities]
        selected_location = {"id": str(location.id), "slug": location.slug, "name": location.name, "village": location.village, "taluka": location.taluka, "district": location.district, "state": location.state, "pincode": location.pincode, "latitude": float(location.latitude), "longitude": float(location.longitude), "is_demo": True}
        return {"is_demo": True, "disclaimer": DISCLAIMER, "selected_location": selected_location, "radius_km": radius, "summary": {"location": "{}, {}, {}".format(location.village, location.taluka, location.district), "radius_km": radius, "business_points_considered": len(local_businesses), "institutions_considered": len(institutions), "amenities_considered": len(amenities), "lower_competition_categories": lower, "higher_demand_categories": higher, "strong_market_access_categories": strong_access}, "businesses": results, "map_points": map_points}

    @staticmethod
    def _market_access(amenities):
        score = 0
        for kind, weight in ACCESS_WEIGHTS.items():
            distances = [distance for item, distance in amenities if item.amenity_type == kind]
            if distances:
                nearest = min(distances)
                score += weight if nearest <= 2 else weight * .65 if nearest <= 5 else weight * .35
        return clamp_score(score)

    @staticmethod
    def _demand(slug, location, reach, access, institutions, amenities, competition):
        education = institutions["SCHOOL"] + institutions["COLLEGE"]
        agriculture, commercial = location.agriculture_intensity_signal, location.commercial_activity_signal
        if slug == "tailoring-alteration": value = reach * .35 + commercial * .25 + education * 8 + access * .2
        elif slug == "mobile-repair-accessories": value = commercial * .35 + education * 7 + access * .3 + reach * .2
        elif slug == "kirana-general-store": value = reach * .55 + commercial * .3 + access * .2 - competition * .25
        elif slug == "dairy-enterprise": value = agriculture * .5 + (15 if "COLLECTION_CENTRE" in amenities else 0) + access * .3
        elif slug == "poultry-enterprise": value = agriculture * .45 + reach * .25 + access * .3
        elif slug == "flour-mill": value = agriculture * .4 + reach * .35 + (100 - competition) * .25
        elif slug == "food-processing-unit": value = agriculture * .35 + access * .35 + (15 if {"WAREHOUSE", "COLD_STORAGE"} & amenities else 0) + commercial * .15
        else: value = agriculture * .5 + access * .3 + (100 - competition) * .2
        return clamp_score(value)

    @staticmethod
    def _supply_chain(slug, agriculture, access, amenities):
        if slug == "dairy-enterprise": value = access * .35 + agriculture * .25 + (25 if AmenityType.COLLECTION_CENTRE in amenities else 0) + (15 if AmenityType.COLD_STORAGE in amenities else 0)
        elif slug == "food-processing-unit": value = access * .35 + agriculture * .2 + (20 if AmenityType.WAREHOUSE in amenities else 0) + (20 if AmenityType.COLD_STORAGE in amenities else 0)
        elif slug in {"poultry-enterprise", "flour-mill", "agri-equipment-rental"}: value = access * .55 + agriculture * .45
        else: value = access * .8 + (20 if AmenityType.MARKET in amenities else 0)
        return clamp_score(value)

    @staticmethod
    def _threats(slug, competition, access, supply, amenities):
        threats = []
        if competition >= 50: threats.append({"code": "HIGH_COMPETITION", "explanation": "Demonstration competitor concentration is high within the measured rings."})
        if access < 45: threats.append({"code": "LOW_MARKET_ACCESS", "explanation": "Few strong market or transport access signals are nearby."})
        if supply < 45: threats.append({"code": "WEAK_SUPPLY_CHAIN", "explanation": "Available access and business-specific supply signals are limited."})
        if not amenities & DISTRIBUTION_TYPES: threats.append({"code": "LIMITED_DISTRIBUTION_ACCESS", "explanation": "No mapped demonstration distribution channel falls within the selected radius."})
        if slug in {"dairy-enterprise", "poultry-enterprise", "food-processing-unit", "agri-equipment-rental"}: threats.append({"code": "SEASONAL_DEMAND", "explanation": "Agricultural cycles and seasonal conditions may affect demand or inputs."})
        if slug == "dairy-enterprise" and AmenityType.COLLECTION_CENTRE in amenities: threats.append({"code": "DEPENDENCE_ON_COLLECTION_POINT", "explanation": "Reliance on a limited milk collection channel may create buyer dependency."})
        return threats
