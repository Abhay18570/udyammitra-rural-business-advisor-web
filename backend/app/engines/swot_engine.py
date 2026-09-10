from decimal import Decimal
import re
from app.schemas.baseline_swot import BaselineSwot
from app.schemas.business_analysis import SwotItem


def analyze_swot(context, competition, threats):
    baseline_data = context.business.catalog_snapshot.get('baseline_swot')
    baseline = BaselineSwot.model_validate(baseline_data) if baseline_data else None
    result = {key: [] for key in ('strengths', 'weaknesses', 'opportunities', 'threats')}
    def add(quadrant, code, title, explanation, evidence, findings=None, importance=None):
        result[quadrant].append(SwotItem(id='swot.' + code, rule_id=code, category=quadrant,
            title=title, explanation=explanation, source_type=source_type(evidence), evidence_ids=evidence, finding_ids=findings or [], importance=importance,
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
    represented = {finding for items in result.values() for item in items for finding in item.finding_ids}
    for kind in ('skills', 'resources'):
        if any(item.rule_id == 'pending-' + kind for item in result['weaknesses']):
            represented.add('threat.confirm-' + kind)
    for threat in threats:
        # Detailed threats retain every original record. SWOT avoids repeating the same finding,
        # and curated baseline threats replace the generic catalog-risk copies in new analyses.
        if threat.evidence_kind != 'DATA_LIMITATION' and threat.id not in represented and not (baseline and threat.evidence_kind == 'INHERENT_BUSINESS_MODEL'):
            add('threats', threat.rule_id, threat.title, threat.description, threat.evidence_ids, [threat.id], threat.severity)
    if baseline:
        for quadrant in result:
            for item in getattr(baseline, quadrant):
                result[quadrant].append(SwotItem(
                    id=f'swot.baseline.{context.business.slug}.{item.id}', rule_id=f'baseline.{context.business.slug}.{item.id}',
                    category=quadrant, title=item.title, explanation=item.description,
                    source_type='BUSINESS_BASELINE', importance=item.importance,
                    evidence_ids=['catalog.baseline_swot'],
                    limitations=['General business guidance; local demand, competitors and outcomes are unverified.'],
                ))
    for quadrant, items in result.items():
        items.sort(key=lambda item: (2 if item.source_type == 'BUSINESS_BASELINE' else 0 if item.importance == 'HIGH' else 1))
        seen_ids, seen_titles, seen_descriptions = set(), set(), set()
        unique = []
        for item in items:
            title, description = normalize(item.title), normalize(item.explanation)
            if item.rule_id in seen_ids or title in seen_titles or description in seen_descriptions:
                continue
            seen_ids.add(item.rule_id); seen_titles.add(title); seen_descriptions.add(description)
            unique.append(item)
        result[quadrant] = unique
    return result


def normalize(text):
    return re.sub(r'[\W_]+', ' ', text.casefold()).strip()


def source_type(evidence):
    for prefix, source in [('market.', 'MARKET'), ('financial.', 'FINANCIAL'), ('profile.', 'PROFILE'), ('catalog.', 'CATALOG')]:
        if any(key.startswith(prefix) for key in evidence):
            return source
    return 'DYNAMIC'
