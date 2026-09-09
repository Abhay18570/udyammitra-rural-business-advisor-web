from decimal import Decimal
from app.business_analysis_rules import BUSINESS_MITIGATIONS
from app.schemas.business_analysis import Threat
from app.engines.nearby_market_engine import fingerprint


def analyze_threats(context, competition):
    findings = []
    def add(code, kind, category, title, description, evidence, mitigation, severity=None, reason=None):
        findings.append(Threat(id='threat.' + code, rule_id=code, threat_type=category, evidence_kind=kind,
            title=title, description=description, severity=severity, severity_reason=reason, likelihood=None,
            evidence_ids=evidence, mitigation=mitigation, source_refs=evidence,
            coverage_warnings=['Not an observed local incident.'] if kind == 'INHERENT_BUSINESS_MODEL' else []))
    catalog = context.business.catalog_snapshot
    mitigation = BUSINESS_MITIGATIONS[context.business.slug]
    for risk in catalog['major_risks']:
        text = risk.casefold()
        category = ('SEASONAL_DEMAND' if 'season' in text else 'RAW_MATERIAL_PRICE' if any(term in text for term in ('feed', 'raw-material', 'price'))
                    else 'CAPITAL' if any(term in text for term in ('payment', 'credit')) else 'INFRASTRUCTURE' if any(term in text for term in ('power', 'water')) else 'OPERATIONAL')
        add('catalog-' + context.business.slug + '-' + fingerprint(risk)[:12], 'INHERENT_BUSINESS_MODEL', category, risk,
            'The selected business catalog identifies this inherent risk; local occurrence and likelihood are unverified.',
            ['catalog.risks'], mitigation)
    for kind in ('skills', 'resources'):
        matches = getattr(context.entrepreneur, kind)
        pending = [m.requirement for m in matches if m.status != 'CONFIRMED_SELF_REPORTED']
        if pending:
            add('confirm-' + kind, 'SELF_REPORTED', 'SKILL' if kind == 'skills' else 'INFRASTRUCTURE',
                'Confirm required ' + kind, 'Not explicitly recorded: ' + ', '.join(pending), ['profile.' + kind],
                'Confirm access or training before committing investment. Broad profile selections are tentative.', 'MEDIUM',
                'At least one catalog requirement lacks an explicit self-report.')
    if context.business.slug == 'tailoring-alteration':
        add('tailoring-skill-dependency', 'INHERENT_BUSINESS_MODEL', 'SKILL', 'Stitching and measurement dependency',
            'The catalog requires stitching and garment measurement capabilities; quality depends on maintaining these skills.',
            ['catalog.requirements'], mitigation)
    if context.business.slug == 'flour-mill':
        add('mill-maintenance', 'INHERENT_BUSINESS_MODEL', 'OPERATIONAL', 'Maintenance dependency',
            'The catalog operating requirements call for preventive maintenance.', ['catalog.requirements'], mitigation)
    for code, value, title, evidence in [
        ('setup-gap', context.financial.alignment.funding_gap, 'Estimated setup capacity shortfall', 'financial.setup'),
        ('scheme-gap', context.scheme.scheme_financing_gap, 'Scheme loan-cap shortfall', 'financial.scheme')]:
        if value is not None and Decimal(value) > 0:
            add(code, 'SELF_REPORTED', 'CAPITAL', title, 'The saved funding assumptions leave a shortfall of ₹' + value + '.',
                [evidence], 'Review the project scope or additional contribution for the same project; financing is not sanctioned.',
                'HIGH', 'A positive calculated funding shortfall leaves this planning structure incomplete.')
    if context.budget.consistency_status == 'DIFFERENT':
        add('budget-different', 'SELF_REPORTED', 'CAPITAL', 'Profile capital differs from saved margin',
            'Current own capital and the saved financial margin are different amounts.', ['profile.budget'],
            'Reconcile the saved financial scenario with the amount you intend to invest.', 'MEDIUM', 'The two declared amounts differ.')
    if competition['classification'] in {'HIGH_MAPPED_PRESSURE', 'MODERATE_MAPPED_PRESSURE'}:
        add('mapped-pressure', 'OBSERVED_LOCAL', 'COMPETITION', 'Provisional mapped competitor pressure',
            '{} mapped direct competitors within {} km; mapped density {:.4f}/km².'.format(competition['direct_count'], competition['selected_radius_km'], competition['mapped_density']),
            ['market.direct', 'market.quality'], 'Compare services and visit mapped establishments before deciding how to differentiate.',
            'HIGH' if competition['classification'] == 'HIGH_MAPPED_PRESSURE' else 'MEDIUM', competition['classification_basis'])
    add('osm-coverage', 'DATA_LIMITATION', 'DATA_LIMITATION', 'Incomplete real-world mapping coverage',
        'A complete provider query is not a complete competitor census. Locality and representative centres are approximate.',
        ['market.quality'], 'Validate mapped evidence locally; absence of mapped records does not establish absence of competitors.')
    if context.market.source.cache_status == 'STALE_CACHE':
        add('stale-market', 'DATA_LIMITATION', 'DATA_LIMITATION', 'Older cached market evidence',
            'Provider refresh was unavailable; current competition classification is withheld.', ['market.quality'], 'Retry later to refresh market evidence.')
    return findings
