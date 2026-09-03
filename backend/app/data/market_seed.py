from decimal import Decimal

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.market_config import DEMO_MARKET_DATA_VERSION
from app.models.business import BusinessProfile
from app.models.market import AmenityType, DemoAmenity, DemoInstitution, DemoLocalBusiness, DemoLocation, InstitutionType

LOCATIONS = [
    {"slug": "karad-satara", "name": "Karad", "village": "Karad", "taluka": "Karad", "district": "Satara", "state": "Maharashtra", "pincode": "415110", "latitude": "17.285000", "longitude": "74.184000", "settlement_density_signal": 72, "agriculture_intensity_signal": 70, "commercial_activity_signal": 76},
    {"slug": "satara-satara", "name": "Satara", "village": "Satara", "taluka": "Satara", "district": "Satara", "state": "Maharashtra", "pincode": "415001", "latitude": "17.680500", "longitude": "74.018300", "settlement_density_signal": 82, "agriculture_intensity_signal": 56, "commercial_activity_signal": 84},
    {"slug": "wai-satara", "name": "Wai", "village": "Wai", "taluka": "Wai", "district": "Satara", "state": "Maharashtra", "pincode": "412803", "latitude": "17.952000", "longitude": "73.890000", "settlement_density_signal": 61, "agriculture_intensity_signal": 68, "commercial_activity_signal": 58},
    {"slug": "phaltan-satara", "name": "Phaltan", "village": "Phaltan", "taluka": "Phaltan", "district": "Satara", "state": "Maharashtra", "pincode": "415523", "latitude": "17.991000", "longitude": "74.431000", "settlement_density_signal": 65, "agriculture_intensity_signal": 82, "commercial_activity_signal": 63},
    {"slug": "patan-satara", "name": "Patan", "village": "Patan", "taluka": "Patan", "district": "Satara", "state": "Maharashtra", "pincode": "415206", "latitude": "17.375000", "longitude": "73.901000", "settlement_density_signal": 48, "agriculture_intensity_signal": 86, "commercial_activity_signal": 43},
]

BUSINESS_SLUGS = ["tailoring-alteration", "mobile-repair-accessories", "kirana-general-store", "dairy-enterprise", "poultry-enterprise", "flour-mill", "food-processing-unit", "agri-equipment-rental"]
BUSINESS_OFFSETS = [
    ("mobile-repair-accessories", .002, .001), ("kirana-general-store", -.003, .002), ("tailoring-alteration", .006, -.004), ("kirana-general-store", -.009, -.005),
    ("dairy-enterprise", .012, .008), ("flour-mill", -.015, .009), ("mobile-repair-accessories", .018, -.012), ("poultry-enterprise", -.021, -.013),
    ("food-processing-unit", .027, .016), ("tailoring-alteration", -.031, .018), ("agri-equipment-rental", .036, -.022), ("kirana-general-store", -.041, -.025),
    ("dairy-enterprise", .047, .028), ("flour-mill", -.053, .031), ("poultry-enterprise", .059, -.034), ("mobile-repair-accessories", -.064, -.039),
    ("food-processing-unit", .071, .043), ("agri-equipment-rental", -.076, .047), ("tailoring-alteration", .082, -.052), ("kirana-general-store", -.086, -.055),
]
INSTITUTIONS = [
    ("Central School", InstitutionType.SCHOOL, .004, -.002), ("Junior College", InstitutionType.COLLEGE, -.011, .006),
    ("Primary Health Centre", InstitutionType.PRIMARY_HEALTH_CENTRE, .018, .012), ("Cooperative Bank", InstitutionType.BANK, -.026, -.014),
    ("Gram Panchayat Office", InstitutionType.GRAM_PANCHAYAT, .035, .019), ("Community Hospital", InstitutionType.HOSPITAL, -.052, .028),
]
AMENITIES = [
    ("Local Market", AmenityType.MARKET, .003, .004), ("Bus Stand", AmenityType.BUS_STAND, -.009, .007),
    ("State Highway Access", AmenityType.MAJOR_ROAD, .016, -.011), ("Transport Depot", AmenityType.TRANSPORT_NODE, -.028, -.017),
    ("Agricultural Market", AmenityType.AGRI_MARKET, .044, .025), ("Milk Collection Centre", AmenityType.COLLECTION_CENTRE, -.061, .037),
    ("Rural Warehouse", AmenityType.WAREHOUSE, .073, -.041), ("Cold Storage", AmenityType.COLD_STORAGE, -.084, -.049),
]


def point(latitude, longitude):
    return WKTElement("POINT({} {})".format(longitude, latitude), srid=4326)


def _upsert(db, model, lookup, values, counts, bucket):
    item = db.scalar(select(model).filter_by(**lookup))
    if item is None:
        db.add(model(**values))
        counts[bucket]["created"] += 1
        return
    changed = False
    for field, value in values.items():
        if field == "geo_point":
            continue
        if getattr(item, field) != value:
            setattr(item, field, value)
            changed = True
    if changed and "geo_point" in values:
        item.geo_point = values["geo_point"]
    counts[bucket]["updated" if changed else "unchanged"] += 1


def seed_market_data(db: Session):
    counts = {name: {"created": 0, "updated": 0, "unchanged": 0} for name in ("locations", "businesses", "institutions", "amenities")}
    profiles = {item.slug: item for item in db.scalars(select(BusinessProfile).where(BusinessProfile.slug.in_(BUSINESS_SLUGS))).all()}
    if len(profiles) != len(BUSINESS_SLUGS):
        raise RuntimeError("Seed the complete business catalog before market demonstration data.")
    for location_data in LOCATIONS:
        values = {**location_data, "latitude": Decimal(location_data["latitude"]), "longitude": Decimal(location_data["longitude"]), "geo_point": point(location_data["latitude"], location_data["longitude"]), "is_active": True, "is_demo": True}
        _upsert(db, DemoLocation, {"slug": location_data["slug"]}, values, counts, "locations")
        db.flush()
        location = db.scalar(select(DemoLocation).where(DemoLocation.slug == location_data["slug"]))
        lat, lon = Decimal(location_data["latitude"]), Decimal(location_data["longitude"])
        for index, (slug, lat_offset, lon_offset) in enumerate(BUSINESS_OFFSETS, 1):
            profile = profiles[slug]
            item_lat, item_lon = lat + Decimal(str(lat_offset)), lon + Decimal(str(lon_offset))
            seed_key = "{}-{:02d}".format(slug, index)
            values = {"demo_location_id": location.id, "business_profile_id": profile.id, "seed_key": seed_key, "name": "{} {}".format(location.name, profile.name), "category": profile.category, "business_type": profile.business_type, "latitude": item_lat, "longitude": item_lon, "geo_point": point(item_lat, item_lon), "source_label": "Curated demonstration market data ({})".format(DEMO_MARKET_DATA_VERSION), "is_demo": True, "is_active": True}
            _upsert(db, DemoLocalBusiness, {"demo_location_id": location.id, "seed_key": seed_key}, values, counts, "businesses")
        for name, kind, lat_offset, lon_offset in INSTITUTIONS:
            item_lat, item_lon = lat + Decimal(str(lat_offset)), lon + Decimal(str(lon_offset))
            full_name = "{} {}".format(location.name, name)
            values = {"demo_location_id": location.id, "name": full_name, "institution_type": kind, "latitude": item_lat, "longitude": item_lon, "geo_point": point(item_lat, item_lon), "is_demo": True, "is_active": True}
            _upsert(db, DemoInstitution, {"demo_location_id": location.id, "name": full_name}, values, counts, "institutions")
        for name, kind, lat_offset, lon_offset in AMENITIES:
            item_lat, item_lon = lat + Decimal(str(lat_offset)), lon + Decimal(str(lon_offset))
            full_name = "{} {}".format(location.name, name)
            values = {"demo_location_id": location.id, "name": full_name, "amenity_type": kind, "latitude": item_lat, "longitude": item_lon, "geo_point": point(item_lat, item_lon), "is_demo": True, "is_active": True}
            _upsert(db, DemoAmenity, {"demo_location_id": location.id, "name": full_name}, values, counts, "amenities")
    db.commit()
    return counts
