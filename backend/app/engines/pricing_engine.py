from decimal import Decimal
from app.utils.money import parse_inr


def money(value):
    return format(parse_inr(value), '.2f')


def analyze_pricing(assumptions):
    result = {'status': 'INSUFFICIENT_PRICING_ASSUMPTIONS', 'strategy': 'Indicative cost-based planning; no observed local prices.',
        'items': [], 'assumptions': [], 'missing_assumptions': [],
        'demographic_status': 'VERIFIED_DATA_UNAVAILABLE', 'local_price_status': 'LOCAL_PRICE_DATA_UNAVAILABLE',
        'purchasing_power_status': 'PURCHASING_POWER_DATA_UNAVAILABLE', 'purchasing_power_adjustment': None,
        'competitor_price_adjustment': None, 'evidence_ids': ['pricing.assumptions', 'data.demographics'],
        'warnings': ['Planning estimates do not establish local selling prices or repayment affordability.', 'Cost coverage depends on the supplied labor, maintenance and overhead assumptions.'],
        'aggregate_break_even': None}
    items, fixed = assumptions.items, assumptions.monthly_fixed_cost
    if not items or fixed is None:
        result['missing_assumptions'] = ['Explicit product/service and unit', 'Unit variable cost', 'Monthly volume', 'Monthly fixed cost and allocation weights', 'Target selling-price margin range']
        return result
    if sum(p.overhead_weight for p in items) != 1 or any(p.allocated_monthly_fixed_cost != fixed * p.overhead_weight for p in items):
        result['missing_assumptions'] = ['Valid overhead weights summing to 1 and allocations matching the shared fixed cost']
        return result
    if any(p.monthly_volume <= 0 or len(p.target_margin_range) != 2 or not all(m.is_finite() and 0 <= m < 1 for m in p.target_margin_range) or p.target_margin_range[0] > p.target_margin_range[1] for p in items):
        result['missing_assumptions'] = ['Positive monthly volumes and ordered finite margins from 0 inclusive to 1 exclusive']
        return result
    for item in items:
        overhead = item.allocated_monthly_fixed_cost / item.monthly_volume
        cost = item.variable_unit_cost + overhead
        low, high = item.target_margin_range
        target_margin = (low + high) / 2
        price = parse_inr(cost / (1 - target_margin))
        contribution = price - item.variable_unit_cost
        result['items'].append({'name': item.name, 'unit': item.unit, 'planning_cost_per_unit': money(cost),
            'allocated_overhead_per_unit': money(overhead), 'recommended_min': money(cost / (1 - low)),
            'recommended_target': money(price), 'recommended_max': money(cost / (1 - high)),
            'target_margin': str(target_margin), 'unit_contribution': money(contribution),
            'operating_break_even_volume': str(item.allocated_monthly_fixed_cost / contribution) if contribution > 0 else None,
            'source': item.source, 'version': item.version, 'evidence_ids': ['pricing.assumptions']})
    result['status'] = 'CALCULATED_FROM_PLANNING_ASSUMPTIONS'
    result['assumptions'] = [p.model_dump(mode='json') for p in items]
    if len(items) > 1:
        result['warnings'].append('No aggregate break-even across products without an explicit sales mix; per-item figures use allocated overhead.')
    return result
