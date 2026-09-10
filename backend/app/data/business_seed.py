from decimal import Decimal
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from copy import deepcopy
from app.data.baseline_swot import BASELINE_SWOT
from app.models.business import BusinessCategory, BusinessProfile, BusinessType
from app.schemas.business import BusinessDetail


def money(value: int) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"))


BUSINESS_SEEDS: List[Dict] = [
    {
        "slug": "tailoring-alteration", "name": "Tailoring & Alteration Centre", "category": BusinessCategory.SERVICES, "business_type": BusinessType.SERVICE,
        "short_description": "Stitching, alteration and basic garment services for households, schools and local institutions.",
        "detailed_description": "A neighbourhood tailoring centre can serve recurring clothing repair, custom stitching and uniform needs. The model may begin from a home workspace and expand as demand and skill capacity grow.",
        "minimum_capital": money(50000), "maximum_capital": money(250000), "estimated_setup_cost_min": money(40000), "estimated_setup_cost_max": money(180000), "working_capital_min": money(10000), "working_capital_max": money(70000),
        "required_skills": ["Basic stitching", "Garment measurement", "Customer service"], "preferred_skills": ["Pattern cutting", "Embroidery", "Basic bookkeeping"],
        "required_resources": ["Clean workspace", "Reliable electricity"], "optional_resources": ["Shop frontage", "Internet access", "Storage space"],
        "equipment": ["Sewing machine", "Cutting table", "Iron and ironing board", "Scissors and measuring tools"],
        "customer_segments": ["Local households", "Students and schools", "Women’s groups", "Local institutions"],
        "market_drivers": ["Regular alteration needs", "School uniform demand", "Festival and wedding seasons"],
        "competition_factors": ["Existing local tailors", "Ready-made garment availability", "Service quality and delivery time"],
        "supply_chain_factors": ["Access to fabric and thread suppliers", "Availability of machine repair services"],
        "major_risks": ["Seasonal order fluctuations", "Machine breakdown", "Delayed customer payments"],
        "required_registrations": ["Local shop or establishment registration may apply", "Udyam registration may be considered where appropriate", "Tax registration may depend on turnover and applicable rules"],
        "operating_requirements": ["Consistent measurement records", "Clear delivery commitments", "Safe electrical setup", "Routine machine maintenance"],
    },
    {
        "slug": "mobile-repair-accessories", "name": "Mobile Repair & Accessories", "category": BusinessCategory.SERVICES, "business_type": BusinessType.SERVICE,
        "short_description": "Repair services and essential mobile accessories for residents, farmers, students and small businesses.",
        "detailed_description": "A mobile repair outlet addresses frequent device faults and access to chargers, cables, cases and screen protection. Trust, technical skill and responsible handling of customer data are central to the model.",
        "minimum_capital": money(75000), "maximum_capital": money(300000), "estimated_setup_cost_min": money(60000), "estimated_setup_cost_max": money(220000), "working_capital_min": money(15000), "working_capital_max": money(80000),
        "required_skills": ["Mobile repair basics", "Customer service"], "preferred_skills": ["Electronics troubleshooting", "Digital payments", "Inventory management"],
        "required_resources": ["Small shop or workspace", "Reliable electricity"], "optional_resources": ["Internet access", "Secure storage", "High-footfall location"],
        "equipment": ["Repair toolkit", "Soldering station", "Multimeter", "Magnification lamp", "Spare parts and accessories inventory"],
        "customer_segments": ["Students", "Farmers", "Local residents", "Small businesses"],
        "market_drivers": ["Smartphone usage", "Distance from service centres", "Cost of replacing devices", "Need for quick repairs"],
        "competition_factors": ["Existing repair shops", "Authorised service centres", "Informal technicians", "Repair turnaround time"],
        "supply_chain_factors": ["Spare-part availability", "Distributor access", "Accessory quality and replacement terms"],
        "major_risks": ["Rapid device changes", "Poor-quality spare parts", "Customer data exposure", "Warranty liability"],
        "required_registrations": ["Local shop or establishment registration may apply", "E-waste handling obligations should be checked", "Tax registration may depend on turnover and applicable rules"],
        "operating_requirements": ["Secure device intake records", "Customer consent before repair", "Safe soldering and electrical practices", "Responsible disposal of damaged parts"],
    },
    {
        "slug": "kirana-general-store", "name": "Kirana / General Store", "category": BusinessCategory.RETAIL, "business_type": BusinessType.RETAIL,
        "short_description": "Daily essentials retail serving nearby households with convenient, dependable stock availability.",
        "detailed_description": "A kirana store supplies frequently purchased food and household essentials. Location, inventory discipline, supplier terms and customer trust are more important than carrying an excessively broad opening stock.",
        "minimum_capital": money(150000), "maximum_capital": money(800000), "estimated_setup_cost_min": money(90000), "estimated_setup_cost_max": money(350000), "working_capital_min": money(60000), "working_capital_max": money(450000),
        "required_skills": ["Retail operations", "Basic arithmetic", "Customer service"], "preferred_skills": ["Inventory management", "Digital payments", "Supplier negotiation"],
        "required_resources": ["Accessible shop space", "Secure storage"], "optional_resources": ["Refrigerator", "Delivery vehicle", "Internet access"],
        "equipment": ["Shelving and counters", "Weighing scale", "Billing supplies", "Storage containers", "Fire extinguisher"],
        "customer_segments": ["Nearby households", "Farm workers", "Students", "Small eateries"],
        "market_drivers": ["Population within walking distance", "Daily essentials demand", "Convenience and opening hours"],
        "competition_factors": ["Nearby kirana stores", "Weekly markets", "Supermarkets and delivery services", "Price and credit practices"],
        "supply_chain_factors": ["Wholesaler access", "Delivery frequency", "Shelf life and stock rotation", "Supplier credit terms"],
        "major_risks": ["Expired inventory", "Excessive customer credit", "Price volatility", "Stock theft or damage"],
        "required_registrations": ["Local shop or establishment registration may apply", "Food registration may apply when selling food products", "Legal metrology requirements may apply to weighing equipment", "Tax registration may depend on turnover and applicable rules"],
        "operating_requirements": ["Daily stock monitoring", "Expiry-date checks", "Clean food storage", "Transparent pricing and credit records"],
    },
    {
        "slug": "dairy-enterprise", "name": "Dairy Enterprise", "category": BusinessCategory.AGRICULTURE, "business_type": BusinessType.AGRI_ALLIED,
        "short_description": "Small-scale milk production built around healthy animals, reliable feed, hygiene and assured milk collection.",
        "detailed_description": "A dairy enterprise can supply milk through collection centres, cooperatives or direct local channels. Animal health, year-round fodder, water and hygienic handling determine operational reliability.",
        "minimum_capital": money(200000), "maximum_capital": money(1000000), "estimated_setup_cost_min": money(160000), "estimated_setup_cost_max": money(800000), "working_capital_min": money(40000), "working_capital_max": money(200000),
        "required_skills": ["Livestock care", "Clean milk handling", "Feed management"], "preferred_skills": ["Animal health observation", "Record keeping", "Fodder planning"],
        "required_resources": ["Cattle shed", "Reliable water", "Fodder access"], "optional_resources": ["Own agricultural land", "Chaff cutter", "Milk cooling access"],
        "equipment": ["Milk cans", "Feeding and watering equipment", "Cleaning tools", "Basic animal-care supplies"],
        "customer_segments": ["Milk cooperatives", "Collection centres", "Local households", "Tea shops and eateries"],
        "market_drivers": ["Reliable milk procurement", "Local consumption", "Access to veterinary services", "Fodder availability"],
        "competition_factors": ["Existing milk suppliers", "Procurement price and quality testing", "Distance to collection point"],
        "supply_chain_factors": ["Fodder and feed prices", "Veterinary medicine access", "Milk collection schedule", "Cold-chain availability"],
        "major_risks": ["Animal illness", "Feed cost increases", "Milk spoilage", "Water scarcity"],
        "required_registrations": ["Local livestock and dairy requirements should be checked", "Food registration may apply for direct sale or processing", "Waste-management and local-body requirements may apply"],
        "operating_requirements": ["Veterinary care plan", "Daily hygiene routine", "Animal and milk records", "Safe manure and wastewater management"],
    },
    {
        "slug": "poultry-enterprise", "name": "Poultry Enterprise", "category": BusinessCategory.AGRICULTURE, "business_type": BusinessType.AGRI_ALLIED,
        "short_description": "Managed egg or bird production requiring biosecurity, feed planning and dependable buyer access.",
        "detailed_description": "A small poultry unit may focus on eggs, broilers or locally suitable birds. The chosen production cycle should match buyer demand, housing capacity, veterinary access and the entrepreneur’s ability to manage biosecurity.",
        "minimum_capital": money(150000), "maximum_capital": money(750000), "estimated_setup_cost_min": money(110000), "estimated_setup_cost_max": money(550000), "working_capital_min": money(40000), "working_capital_max": money(200000),
        "required_skills": ["Bird care", "Feed and water management", "Basic biosecurity"], "preferred_skills": ["Flock record keeping", "Disease symptom observation", "Buyer coordination"],
        "required_resources": ["Ventilated poultry shed", "Reliable water", "Electricity"], "optional_resources": ["Own land", "Feed storage", "Backup power"],
        "equipment": ["Feeders and drinkers", "Brooding equipment", "Cleaning and disinfection tools", "Crates or egg trays"],
        "customer_segments": ["Local households", "Meat and egg retailers", "Hotels and eateries", "Wholesale buyers"],
        "market_drivers": ["Local egg and poultry consumption", "Reliable buyer network", "Feed availability", "Veterinary support"],
        "competition_factors": ["Commercial poultry supply", "Existing local producers", "Buyer price sensitivity", "Product consistency"],
        "supply_chain_factors": ["Chick or bird availability", "Feed price and quality", "Medicine access", "Transport to buyers"],
        "major_risks": ["Disease outbreak", "Feed price volatility", "Mortality", "Market price fluctuations"],
        "required_registrations": ["Local livestock or poultry permissions should be checked", "Food and trade requirements may apply based on sales activity", "Waste and environmental requirements may vary by unit size and location"],
        "operating_requirements": ["Controlled visitor access", "Vaccination and health plan", "Daily flock records", "Safe litter and mortality disposal"],
    },
    {
        "slug": "flour-mill", "name": "Flour Mill", "category": BusinessCategory.FOOD_PROCESSING, "business_type": BusinessType.PROCESSING,
        "short_description": "Local grain grinding services for households, farmers and small food businesses.",
        "detailed_description": "A flour mill converts customer-supplied or procured grain into flour. Consistent grinding quality, dust control, equipment safety and reliable electricity are essential for customer retention.",
        "minimum_capital": money(250000), "maximum_capital": money(1200000), "estimated_setup_cost_min": money(210000), "estimated_setup_cost_max": money(1000000), "working_capital_min": money(40000), "working_capital_max": money(200000),
        "required_skills": ["Machine operation", "Grain handling", "Basic customer service"], "preferred_skills": ["Equipment maintenance", "Food hygiene", "Inventory management"],
        "required_resources": ["Commercial workspace", "Suitable electrical connection", "Dry storage"], "optional_resources": ["Three-phase power", "Delivery vehicle", "Grain procurement network"],
        "equipment": ["Flour mill machine", "Weighing scale", "Dust collection equipment", "Sieves and food-grade containers", "Safety guards"],
        "customer_segments": ["Local households", "Farmers", "Bakeries", "Small eateries"],
        "market_drivers": ["Local grain production", "Preference for freshly milled flour", "Distance to other mills"],
        "competition_factors": ["Existing flour mills", "Packaged flour availability", "Grinding charges", "Product consistency"],
        "supply_chain_factors": ["Machine parts and service access", "Packaging availability", "Grain sourcing when retailing flour"],
        "major_risks": ["Machine injury", "Dust exposure", "Power interruption", "Product contamination"],
        "required_registrations": ["Food registration or licence may apply", "Local trade and establishment registration may apply", "Electrical, fire and pollution-control requirements should be checked for the proposed scale", "Legal metrology requirements may apply"],
        "operating_requirements": ["Machine guarding and operator training", "Dust and pest control", "Food-grade cleaning schedule", "Preventive maintenance"],
    },
    {
        "slug": "food-processing-unit", "name": "Food Processing Unit", "category": BusinessCategory.FOOD_PROCESSING, "business_type": BusinessType.PROCESSING,
        "short_description": "Small-batch processing of locally available produce into packaged, shelf-stable food products.",
        "detailed_description": "A small food processing unit may produce spices, pickles, snacks, preserves or other locally relevant goods. The product range should be narrow initially and supported by standard recipes, hygiene controls and tested packaging.",
        "minimum_capital": money(200000), "maximum_capital": money(1000000), "estimated_setup_cost_min": money(150000), "estimated_setup_cost_max": money(750000), "working_capital_min": money(50000), "working_capital_max": money(250000),
        "required_skills": ["Food preparation", "Food hygiene", "Quality consistency"], "preferred_skills": ["Packaging and labelling", "Recipe standardisation", "Retail sales"],
        "required_resources": ["Hygienic workspace", "Reliable water and electricity", "Dry storage"], "optional_resources": ["Cold storage", "Own farm produce", "Delivery vehicle"],
        "equipment": ["Product-appropriate processing equipment", "Food-grade utensils", "Weighing scale", "Sealing or packaging machine", "Cleaning equipment"],
        "customer_segments": ["Local households", "Retail stores", "Hotels and eateries", "Regional distributors"],
        "market_drivers": ["Availability of local produce", "Demand for convenient foods", "Product shelf life", "Retail and institutional access"],
        "competition_factors": ["Established packaged brands", "Local home producers", "Price and taste preference", "Packaging quality"],
        "supply_chain_factors": ["Seasonal raw-material availability", "Food-grade packaging supply", "Transport and storage conditions"],
        "major_risks": ["Food contamination", "Inconsistent quality", "Raw-material price changes", "Unsold short-shelf-life inventory"],
        "required_registrations": ["Food registration or licence may apply based on activity and scale", "Packaging and labelling rules should be verified", "Local trade, fire, environmental and tax requirements may apply"],
        "operating_requirements": ["Documented recipes and batch records", "Cleaning and pest-control plan", "Shelf-life assessment", "Traceable sourcing and labelling"],
    },
    {
        "slug": "agri-equipment-rental", "name": "Agricultural Equipment Rental", "category": BusinessCategory.AGRICULTURE, "business_type": BusinessType.RENTAL,
        "short_description": "Shared access to farm machinery and tools for farmers who prefer renting over purchasing equipment.",
        "detailed_description": "An equipment rental enterprise makes selected farm machinery available by time, acreage or job. Equipment choice should follow local crop cycles and farmer demand, with careful booking, operator safety and maintenance controls.",
        "minimum_capital": money(500000), "maximum_capital": money(3000000), "estimated_setup_cost_min": money(450000), "estimated_setup_cost_max": money(2700000), "working_capital_min": money(50000), "working_capital_max": money(300000),
        "required_skills": ["Farm equipment operation", "Scheduling", "Basic maintenance"], "preferred_skills": ["Driving", "Customer coordination", "Cost record keeping"],
        "required_resources": ["Secure equipment storage", "Transport access"], "optional_resources": ["Workshop space", "Own vehicle", "Trained equipment operator"],
        "equipment": ["Locally demanded farm implements", "Safety equipment", "Basic maintenance tools", "Booking and usage records"],
        "customer_segments": ["Small and marginal farmers", "Farmer groups", "Tenant farmers", "Agricultural cooperatives"],
        "market_drivers": ["Farm mechanisation needs", "Small landholdings", "Seasonal labour constraints", "Cost of equipment ownership"],
        "competition_factors": ["Other rental providers", "Cooperative or public hiring centres", "Equipment availability during peak season", "Rental and transport charges"],
        "supply_chain_factors": ["Dealer and spare-parts access", "Fuel availability", "Service technician access", "Transport logistics"],
        "major_risks": ["Equipment damage", "Seasonal under-utilisation", "Payment delays", "Operator injury"],
        "required_registrations": ["Local trade or establishment registration may apply", "Vehicle, insurance and operator requirements depend on the equipment offered", "Safety and tax obligations should be checked for the operating model"],
        "operating_requirements": ["Written booking and condition records", "Preventive maintenance schedule", "Trained operators where needed", "Safety briefings and appropriate insurance review"],
    },
]


for _business in BUSINESS_SEEDS:
    _business['baseline_swot'] = deepcopy(BASELINE_SWOT[_business['slug']])

def seed_businesses(db: Session) -> Dict[str, int]:
    created = updated = unchanged = 0
    for data in BUSINESS_SEEDS:
        BusinessDetail.model_validate({"id": "00000000-0000-0000-0000-000000000000", "is_active": True, **data})
        business = db.scalar(select(BusinessProfile).where(BusinessProfile.slug == data["slug"]))
        if business is None:
            db.add(BusinessProfile(**data, is_active=True))
            created += 1
            continue
        changed = False
        for field, value in {**data, "is_active": True}.items():
            if getattr(business, field) != value:
                setattr(business, field, value)
                changed = True
        if changed:
            updated += 1
        else:
            unchanged += 1
    db.commit()
    return {"created": created, "updated": updated, "unchanged": unchanged}


def seed_baseline_swot(db: Session) -> Dict[str, int]:
    """Update only baseline knowledge on existing canonical businesses; never reset catalog edits."""
    updated = unchanged = missing = 0
    try:
        for slug, guidance in BASELINE_SWOT.items():
            business = db.scalar(select(BusinessProfile).where(BusinessProfile.slug == slug))
            if business is None:
                missing += 1
            elif business.baseline_swot == guidance:
                unchanged += 1
            else:
                business.baseline_swot = deepcopy(guidance)
                updated += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {'updated': updated, 'unchanged': unchanged, 'missing': missing}
