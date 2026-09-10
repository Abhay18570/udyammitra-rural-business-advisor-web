"""Curated prototype catalog guidance, never measurements of an entrepreneur's locality."""
from app.schemas.baseline_swot import BaselineSwot

BASELINE_SWOT_VERSION = 'business-baseline-v1'
DISCLOSURE = 'Baseline findings describe common business characteristics. Local findings are shown separately when supported by profile or market evidence.'

# Titles and descriptions remain English, like the existing catalog knowledge.
# No counts, observed demand, local competitors, or guaranteed outcomes are inferred.
_GUIDANCE = {
    'kirana-general-store': [
        [
            ('Recurring demand for daily essentials', 'Everyday grocery and household products can generate repeat customer visits.'),
            ('Wide product mix', 'A kirana store can serve multiple household needs from a single outlet.'),
            ('Customer relationships', 'Local stores can build repeat business through familiarity and convenient service.'),
            ('Flexible inventory', 'Stock quantities and product mix can be adjusted as customer preferences become clearer.'),
        ], [
            ('Inventory management requirement', 'A wide product range requires regular stock monitoring and replenishment.'),
            ('Risk of slow-moving stock', 'Slow-selling products tie up shelf space and cash; review stock movement regularly.'),
            ('Working-capital dependence', 'Money remains tied up in inventory and requires disciplined cash-flow management.'),
            ('Limited differentiation', 'Many essential products may also be available from competing retailers.'),
        ], [
            ('Home delivery and digital ordering', 'Local delivery or messaging-based ordering may improve convenience where practical.'),
            ('Digital payment adoption', 'UPI and other digital payments can make transactions easier for customers.'),
            ('Product expansion', 'Validated demand may support additional household, packaged-food or locally preferred products.'),
            ('Potential institutional sales', 'Offices, schools or small businesses may offer sales channels; verify their presence and purchasing needs first.'),
        ], [
            ('Grocery competition', 'Other kirana stores and supermarkets may compete on price, assortment and convenience where present.'),
            ('Online and quick-commerce competition', 'Delivery platforms may influence customer expectations where such services operate.'),
            ('Supplier price fluctuations', 'Wholesale price changes can affect retail margins.'),
            ('Stock spoilage and expiry', 'Perishable or dated stock may create losses if storage and inventory rotation are poor.'),
        ],
    ],
    'tailoring-alteration': [
        [
            ('Skill-based service with limited inventory', 'Tailoring can earn service income without holding a large range of finished garments.'),
            ('Repeat alteration and fitting needs', 'Clothing adjustments and repairs can bring customers back when service is reliable.'),
            ('Personalized service', 'Measurements, fit and design preferences allow a tailor to adapt work to individual customers.'),
            ('Small-scale operating potential', 'A modest workspace and selected equipment can support a controlled start where suitable.'),
        ], [
            ('Dependence on tailoring skill', 'Fit and finish depend heavily on accurate measurement, cutting and stitching skills.'),
            ('Time-limited capacity', 'Available labour and working hours constrain the number of orders that can be completed.'),
            ('Seasonal order patterns', 'Orders may fluctuate around school terms, festivals and weddings.'),
            ('Equipment dependence', 'Machine downtime can interrupt deliveries unless maintenance and backup arrangements are planned.'),
        ], [
            ('School and uniform stitching', 'Uniform work may offer repeat orders after confirming institutional requirements and buyers.'),
            ('Wedding and festival orders', 'Seasonal clothing needs may support advance bookings where customer interest is verified.'),
            ('Custom garment services', 'Specialized fitting and custom garments may help distinguish the service where skills and demand align.'),
            ('Clothing-shop partnerships', 'Boutiques or clothing shops may refer alteration work where mutually useful arrangements are available.'),
        ], [
            ('Ready-made garment alternatives', 'Ready-made clothing may reduce demand for some custom-stitching services.'),
            ('Competing tailoring services', 'Other tailors may compete on workmanship, turnaround time and price where present.'),
            ('Changing fashion preferences', 'New styles may require ongoing learning and changes to service offerings.'),
            ('Rising input and labour costs', 'Fabric accessories, thread and labour costs may narrow margins on fixed-price orders.'),
        ],
    ],
    'mobile-repair-accessories': [
        [
            ('Device maintenance needs', 'Device faults and wear can create repair demand when customers prefer repair to replacement.'),
            ('Multiple revenue streams', 'Repair work and accessory sales can complement one another.'),
            ('Repeat service relationships', 'Reliable diagnosis and responsible handling can encourage customers to return.'),
            ('Accessories complement repair income', 'Cases, cables and protective products can serve additional customer needs with small individual stock units.'),
        ], [
            ('Technical diagnosis requirement', 'Accurate fault diagnosis requires practical skills and suitable tools.'),
            ('Spare-part availability', 'Unavailable or unsuitable parts can delay repair completion.'),
            ('Frequent model changes', 'Changing devices require updated repair knowledge and careful parts selection.'),
            ('Repair quality and reputation risk', 'Incorrect repairs can lead to rework, disputes and loss of customer trust.'),
        ], [
            ('Screen and battery replacement', 'Replacement services may be useful where supported by skills, safe procedures and suitable parts.'),
            ('Protective accessories', 'Cases and screen protection may complement repair services where customers value them.'),
            ('Setup and software assistance', 'Consent-based device setup and basic software assistance may provide additional service opportunities.'),
            ('Pickup and service partnerships', 'Pickup/drop arrangements or local partnerships may extend reach where practical and secure.'),
        ], [
            ('Authorized service alternatives', 'Authorized service centres may attract customers seeking manufacturer-backed repairs where available.'),
            ('Rapid technology changes', 'New device construction and repair restrictions may make some repairs harder or less economical.'),
            ('Poor-quality spare parts', 'Low-quality or counterfeit parts can cause failures and damage trust.'),
            ('Repair-shop price competition', 'Other repair providers may compete aggressively on price where present.'),
        ],
    ],
    'dairy-enterprise': [
        [
            ('Frequently consumed product', 'Milk can meet recurring household and food-service needs; actual buyers still need confirmation.'),
            ('Potential daily sales', 'Regular production can support frequent sales when collection and buyer arrangements are reliable.'),
            ('Value-added product potential', 'Suitable processing capability may allow milk to be used in higher-value products.'),
            ('Possible agricultural resource fit', 'Agricultural households may already have relevant experience or resources; availability must be verified individually.'),
        ], [
            ('Daily animal-care commitment', 'Feeding, water, cleaning and observation require attention every day.'),
            ('Feed and veterinary costs', 'Animal nutrition and veterinary care create continuing operating expenses.'),
            ('Perishable output', 'Milk needs hygienic handling and reliable collection or cooling arrangements.'),
            ('Variable production', 'Animal health and lactation cycles can change output and cash flow.'),
        ], [
            ('Value-added dairy products', 'Curd, paneer or ghee may offer opportunities after confirming processing capability, safe handling and demand.'),
            ('Household and shop supply', 'Direct supply may be practical where buyers, delivery costs and handling arrangements are verified.'),
            ('Collection-centre linkages', 'Cooperatives or collection centres may provide outlets where available and suitable terms can be agreed.'),
            ('Improved herd management', 'Qualified advice on feeding and herd management may support productivity and animal welfare.'),
        ], [
            ('Animal disease', 'Disease can interrupt production and increase care costs; access to veterinary support matters.'),
            ('Feed-price increases', 'Higher feed and fodder prices can reduce operating margins.'),
            ('Milk-price fluctuations', 'Changes in procurement or selling prices can affect cash flow.'),
            ('Heat and weather stress', 'Heat, weather disruption or gaps in veterinary access can affect animal health and milk output.'),
        ],
    ],
    'poultry-enterprise': [
        [
            ('Relatively short production cycles', 'Some poultry models allow results to be reviewed over relatively short cycles.'),
            ('Egg and poultry food needs', 'Demand may exist for eggs or poultry meat, subject to local buyer and product preferences.'),
            ('Controlled starting scale', 'A suitable flock size can help match early operations to available housing and management capacity.'),
            ('Choice of production model', 'Egg or bird production offers different models that can be selected after assessing resources and buyers.'),
        ], [
            ('Strict flock management', 'Hygiene, biosecurity and routine observation require consistent attention.'),
            ('Feed-cost dependence', 'Feed is a substantial recurring input and needs careful purchasing and usage records.'),
            ('Sensitivity to mortality', 'Bird losses directly reduce saleable output and can undermine a production cycle.'),
            ('Environmental control needs', 'Ventilation, temperature and dependable water are important operational requirements.'),
        ], [
            ('Potential egg supply', 'Regular egg supply may be useful where buyers and distribution arrangements are confirmed.'),
            ('Direct sales channels', 'Household or retail sales may offer alternatives after checking practical demand and handling needs.'),
            ('Measured expansion', 'Successful cycles and verified buyer demand may support gradual expansion.'),
            ('Verified institutional buyers', 'Institutions may offer sales opportunities only after their needs and purchasing arrangements are checked.'),
        ], [
            ('Disease outbreaks', 'Flock disease can cause losses and disrupt sales.'),
            ('Feed-price volatility', 'Feed-price changes may make expected margins less reliable.'),
            ('Product-price fluctuations', 'Egg or bird selling prices can change between planning and sale.'),
            ('Management-related mortality', 'Poor hygiene, water or environmental management can cause substantial bird losses.'),
        ],
    ],
    'flour-mill': [
        [
            ('Essential food-processing service', 'Grain grinding can serve routine food-preparation needs where households use such services.'),
            ('Potential repeat household visits', 'Household grain consumption may create recurring grinding work.'),
            ('Straightforward service model', 'Charging by quantity processed can make the service and its pricing easy to explain.'),
            ('Multiple customer segments', 'Households and small food businesses may both need grinding services where verified.'),
        ], [
            ('Electricity dependence', 'Machine operation relies on a suitable and dependable power supply.'),
            ('Maintenance requirement', 'Grinding equipment needs cleaning, wear checks and planned servicing.'),
            ('Dust and noise management', 'Dust control, safe operation and considerate siting require ongoing attention.'),
            ('Machine-limited throughput', 'Equipment capacity and cleaning time constrain the volume that can be handled.'),
        ], [
            ('Multiple-grain services', 'Suitable machinery may support different grains with appropriate cleaning and handling.'),
            ('Packaged flour', 'Packaging may create another offering after checking quality, shelf life and buyer needs.'),
            ('Food-business service links', 'Nearby food businesses may need grinding services; confirm their actual requirements first.'),
            ('Practical pickup and delivery', 'Collection or delivery may add convenience where volumes and transport costs justify it.'),
        ], [
            ('Other flour mills', 'Competing mills may influence prices and turnaround expectations where present.'),
            ('Power interruptions', 'Electricity disruption can delay customer work and reduce operating hours.'),
            ('Equipment breakdown', 'Unplanned failures may lead to repair costs and lost service time.'),
            ('Branded packaged flour', 'Ready-packaged flour may compete with customer-supplied grain grinding.'),
        ],
    ],
    'food-processing-unit': [
        [
            ('Value addition to raw products', 'Processing can turn suitable agricultural or raw inputs into differentiated products.'),
            ('Product differentiation', 'Recipes, format and consistent quality can help establish a distinct offering.'),
            ('Choice of product categories', 'Several processing models may be possible, depending on skills, equipment and validated demand.'),
            ('Potential local sourcing', 'Locally available inputs may support sourcing if quality and supply reliability are confirmed.'),
        ], [
            ('Quality consistency requirement', 'Recipes and batch controls need discipline to keep products consistent.'),
            ('Packaging and storage costs', 'Suitable packaging and storage add to setup and recurring expenses.'),
            ('Food-safety responsibilities', 'Safe production and applicable compliance requirements require attention before sales begin.'),
            ('Shelf-life management', 'Product stability and storage conditions need assessment to avoid unsuitable or unsold stock.'),
        ], [
            ('Local specialty products', 'Distinctive products may find buyers after validating taste, quality and purchasing interest.'),
            ('Retail and institutional supply', 'Shops or institutions may be channels where their requirements and procurement terms are verified.'),
            ('Packaging and branding improvements', 'Clear, suitable packaging and consistent presentation can help communicate product value.'),
            ('Additional distribution channels', 'Digital or local channels may extend reach where delivery and storage remain practical.'),
        ], [
            ('Raw-material price variation', 'Input-price changes can affect batch costs and margins.'),
            ('Established food brands', 'Established brands may compete through availability, promotion and customer familiarity.'),
            ('Spoilage and quality failures', 'Handling or quality failures may cause waste, returns and loss of trust.'),
            ('Compliance failures', 'Failure to meet applicable requirements can interrupt operations; verify obligations for the actual activity.'),
        ],
    ],
    'agri-equipment-rental': [
        [
            ('Access without equipment ownership', 'Renting can let farmers use suitable machinery without buying it outright.'),
            ('Shared use across customers', 'An asset may serve multiple customers when bookings and transport are coordinated.'),
            ('Income from equipment assets', 'Rental charges can generate income from machinery when utilization covers costs.'),
            ('Seasonal agricultural service needs', 'Farm operations may create time-sensitive equipment needs; actual demand must be checked.'),
        ], [
            ('High acquisition cost', 'Equipment purchases can require substantial initial capital.'),
            ('Repair and maintenance expenses', 'Wear, servicing and spare parts create continuing costs.'),
            ('Seasonal utilization', 'Equipment may stand idle outside relevant crop operations.'),
            ('Scheduling and logistics complexity', 'Bookings, transport and operator availability must align with customer timings.'),
        ], [
            ('Serving surrounding villages', 'A wider service area may be practical where transport costs and verified demand align.'),
            ('Equipment portfolio expansion', 'Additional equipment may be justified by demonstrated utilization and customer needs.'),
            ('Operator-supported services', 'Trained operator support may add value where safe and practical to provide.'),
            ('Farmer-group partnerships', 'Farmer groups may coordinate demand where available and suitable terms can be agreed.'),
        ], [
            ('Peak-season breakdown', 'Equipment failure during short service windows can cause missed bookings and lost income.'),
            ('Fuel-cost increases', 'Higher fuel and transport costs can reduce rental margins.'),
            ('Competing rental providers', 'Other providers or hiring centres may compete on rates and availability where present.'),
            ('Weather-related schedule changes', 'Weather can shift or delay farm operations and affect equipment utilization.'),
        ],
    ],
}

BASELINE_SWOT = {
    slug: BaselineSwot.model_validate({
        'version': BASELINE_SWOT_VERSION,
        **{quadrant: [dict(id=f'{quadrant}-{index+1}', title=title, description=description)
                      for index, (title, description) in enumerate(items)]
           for quadrant, items in zip(('strengths', 'weaknesses', 'opportunities', 'threats'), groups)},
    }).model_dump(mode='json')
    for slug, groups in _GUIDANCE.items()
}
