from decimal import Decimal
from app.schemas.business_analysis import SwotItem


def analyze_swot(context, competition, threats):
    result = {key: [] for key in ('strengths', 'weaknesses', 'opportunities', 'threats')}
    def add(quadrant, code, title, explanation, evidence, findings=None, importance=None):
        result[quadrant].append(SwotItem(id='swot.' + code, rule_id=code, category=quadrant,
            title=title, explanation=explanation, evidence_ids=evidence, finding_ids=findings or [], importance=importance,
            limitations=['Self-reported and planning evidence does not guarantee demand, profitability or loan sanction.']))
    for kind in ('skills', 'resources'):
        matches = getattr(context.entrepreneur, kind)
        confirmed = [m.requirement for m in matches if m.status == 'CONFIRMED_SELF_REPORTED']
        pending = [m.requirement for m in matches if m.status != 'CONFIRMED_SELF_REPORTED']
        if confirmed:
            add('strengths', 'declared-' + kind, 'Declared required ' + kind, ', '.join(confirmed), ['profile.' + kind])
        if pending:
            add('weaknesses', 'pending-' + kind, 'Required ' + kind + ' need confirmation', 'Not explicitly recorded: ' + ', '.join(pending), ['profile.' + kind])
    if context.financial.alignment.setup_cost_coverage_status == 'WITHIN_TYPICAL_RANGE':
        add('strengths', 'setup-alignment', 'Project capacity aligns with catalog setup estimates',
            'Saved project capacity is ₹' + context.financial.feasible_project_cost + '; this is setup alignment, not profitability.', ['financial.setup'])
    for code, amount, evidence in [('setup-gap', context.financial.alignment.funding_gap, 'financial.setup'), ('scheme-gap', context.scheme.scheme_financing_gap, 'financial.scheme')]:
        if amount is not None and Decimal(amount) > 0:
            add('weaknesses', code, 'Setup shortfall' if code == 'setup-gap' else 'Additional contribution required',
                'Calculated shortfall: ₹' + amount + '. Setup and scheme gaps are separate comparisons.', [evidence], ['threat.' + code], 'HIGH')
    if context.budget.consistency_status == 'DIFFERENT':
        add('weaknesses', 'budget-different', 'Reconcile capital assumptions', 'Profile own capital differs from the saved financial margin.', ['profile.budget'], ['threat.budget-different'])
    if competition['related_count'] and context.market.source.cache_status != 'STALE_CACHE':
        add('opportunities', 'related-channels', 'Investigate possible referral or sales channels',
            '{} related businesses are mapped within {} km. These are possible contacts, not proven customers.'.format(competition['related_count'], competition['selected_radius_km']), ['market.related'])
    for threat in threats:
        if threat.evidence_kind != 'DATA_LIMITATION':
            add('threats', threat.rule_id, threat.title, threat.description, threat.evidence_ids, [threat.id], threat.severity)
    return result
