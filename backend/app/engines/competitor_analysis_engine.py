import math
from app.osm_business_rules import BUSINESS_RULES, WEAK_MAPPING_BUSINESSES


def analyze_competition(context):
    market = context.market
    radius = market.radius.selected_km
    direct = sorted(market.competitors, key=lambda p: (p.distance_meters, p.external_type, p.external_id))
    area = math.pi * radius ** 2
    n = len(direct)
    nearest = direct[0] if direct else None
    complete = market.quality.complete_query
    stale = market.source.cache_status == 'STALE_CACHE'
    weak = context.business.slug in WEAK_MAPPING_BUSINESSES or context.business.slug not in BUSINESS_RULES
    density = n / area if complete else None
    if not complete:
        label = 'UNAVAILABLE_INCOMPLETE_COVERAGE'
    elif stale:
        label = 'STALE_EVIDENCE'
    elif weak:
        label = 'UNCLASSIFIED_LIMITED_MAPPING'
    elif not n:
        label = 'NO_MAPPED_DIRECT_EVIDENCE'
    # Equivalent count/area comparisons avoid floating-point pi threshold drift.
    elif n >= 3 * radius ** 2 and nearest.distance_meters <= 500:
        label = 'HIGH_MAPPED_PRESSURE'
    elif n >= radius ** 2 or nearest.distance_meters <= 1000:
        label = 'MODERATE_MAPPED_PRESSURE'
    else:
        label = 'LOW_MAPPED_PRESSURE'
    bands = []
    for lower, upper in [(0, 1), (1, 3), (3, 5), (5, radius)]:
        upper = min(upper, radius)
        if lower >= upper:
            continue
        bands.append({'lower_km': lower, 'upper_km': upper, 'lower_inclusive': lower == 0,
            'count': sum((p.distance_meters >= 0 if lower == 0 else p.distance_meters > lower * 1000) and p.distance_meters <= upper * 1000 for p in direct) if complete else None})
    return {'selected_radius_km': radius, 'area_km2': area, 'direct_count': n if complete else None,
        'related_count': len(market.related_businesses) if complete else None,
        'nearest': nearest.model_dump(mode='json') if nearest and complete else None,
        'average_distance': sum(p.distance_meters for p in direct) / n if n and complete else None,
        'average_distance_unit': 'meters', 'mapped_density': density, 'density_label': 'Mapped direct competitors per km²',
        'distance_bands': bands, 'classification': label, 'provisional': True,
        'classification_basis': 'HIGH: density >= 3/π and nearest <= 0.5 km; MODERATE: density >= 1/π or nearest <= 1 km; otherwise LOW when mapped direct records exist. Uncalibrated planning policy.',
        'evidence_quality': market.quality.model_dump(mode='json'), 'source_freshness': market.source.model_dump(mode='json'),
        'competitor_records': [p.model_dump(mode='json') for p in direct], 'evidence_ids': ['market.direct', 'market.related', 'market.quality']}
