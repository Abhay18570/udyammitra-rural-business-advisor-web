from copy import deepcopy
from decimal import Decimal
from types import SimpleNamespace as NS
import math
import pytest
from app.schemas.business_analysis import PricingAssumptions, PricingItem
from app.engines.pricing_engine import analyze_pricing
from app.engines.profile_evidence import match_requirements
from app.engines.competitor_analysis_engine import analyze_competition
from app.engines.threat_engine import analyze_threats
from app.engines.swot_engine import analyze_swot
from app.business_analysis_rules import BUSINESS_MITIGATIONS
from app.data.business_seed import BUSINESS_SEEDS


class Record(NS):
    def model_dump(self, **kwargs):
        return vars(self)


def context(radius=5, distances=(1500, 4000), related=1, slug='tailoring-alteration', stale=False, complete=True):
    catalog = next(b for b in BUSINESS_SEEDS if b['slug'] == slug)
    return NS(business=NS(slug=slug, catalog_snapshot=catalog),
        market=NS(radius=NS(selected_km=radius), competitors=[Record(distance_meters=d, external_type='node', external_id=str(i)) for i,d in enumerate(distances)], related_businesses=[{}] * related,
            quality=Record(complete_query=complete), source=Record(cache_status='STALE_CACHE' if stale else 'FRESH_CACHE')),
        entrepreneur=NS(skills=match_requirements(['Tailoring'], catalog['required_skills'], 'skills'), resources=match_requirements(['Electricity'], catalog['required_resources'], 'resources')),
        financial=NS(feasible_project_cost='140000.00', alignment=NS(funding_gap='0.00', setup_cost_coverage_status='WITHIN_TYPICAL_RANGE')),
        scheme=NS(scheme_financing_gap='1000.00'), budget=NS(consistency_status='CONSISTENT'))


@pytest.mark.parametrize('radius', [1, 10])
def test_density_normalization(radius):
    result = analyze_competition(context(radius, (100, 500)))
    assert result['area_km2'] == math.pi * radius ** 2
    assert result['mapped_density'] == 2 / (math.pi * radius ** 2)
    assert result['nearest']['distance_meters'] == 100
    assert result['average_distance'] == 300
    assert result['direct_count'] == 2 and result['related_count'] == 1


@pytest.mark.parametrize('radius,distances,expected', [(1, (0,100,500), 'HIGH_MAPPED_PRESSURE'), (1,(501,600,700),'MODERATE_MAPPED_PRESSURE'), (5,(1000,), 'MODERATE_MAPPED_PRESSURE'), (5,(1000.01,), 'LOW_MAPPED_PRESSURE'), (5,(), 'NO_MAPPED_DIRECT_EVIDENCE')])
def test_competition_thresholds(radius, distances, expected):
    assert analyze_competition(context(radius, distances))['classification'] == expected


@pytest.mark.parametrize('changes,expected', [({'stale':True}, 'STALE_EVIDENCE'), ({'complete':False}, 'UNAVAILABLE_INCOMPLETE_COVERAGE'), ({'slug':'dairy-enterprise'}, 'UNCLASSIFIED_LIMITED_MAPPING')])
def test_special_competition_states(changes, expected):
    result = analyze_competition(context(**changes))
    assert result['classification'] == expected
    if changes.get('complete') is False:
        assert result['direct_count'] is result['mapped_density'] is None


def test_distance_bands_boundary_clipping():
    result = analyze_competition(context(8, (0,1000,1000.01,3000,3000.01,5000,5000.01,8000)))
    assert [b['count'] for b in result['distance_bands']] == [2,2,2,2]
    assert len(analyze_competition(context(1,(0,1000)))['distance_bands']) == 1


def test_profile_aliases_are_tentative():
    matches = match_requirements(['Machinery','Land','Electricity'], ['Three-phase power','Cattle shed','Electricity','Water'], 'resources')
    assert [m.status for m in matches] == ['TENTATIVE_ALIAS_MATCH','TENTATIVE_ALIAS_MATCH','CONFIRMED_SELF_REPORTED','NOT_RECORDED']
    assert match_requirements([], ['Tailoring'], 'skills')[0].status == 'NOT_RECORDED'


@pytest.mark.parametrize('slug', list(BUSINESS_MITIGATIONS))
def test_catalog_threats_all_businesses(slug):
    c = context(slug=slug)
    threats = analyze_threats(c, analyze_competition(c))
    inherent = [t for t in threats if t.evidence_kind == 'INHERENT_BUSINESS_MODEL']
    assert set(c.business.catalog_snapshot['major_risks']) <= {t.title for t in inherent}
    assert all(t.mitigation and t.evidence_ids and t.likelihood is None for t in threats)
    assert all(t.severity is None for t in inherent)
    assert any(t.evidence_kind == 'DATA_LIMITATION' for t in threats)


def test_swot_evidence_and_financial_gaps():
    c=context()
    c.financial.alignment.funding_gap='10000.00'
    c.budget.consistency_status='DIFFERENT'
    c.entrepreneur.skills=match_requirements(['Tailoring'], ['Tailoring'], 'skills')
    competition=analyze_competition(c)
    threats=analyze_threats(c,competition)
    result=analyze_swot(c,competition,threats)
    assert {'setup-gap','scheme-gap','budget-different'} <= {i.rule_id for i in result['weaknesses']}
    assert 'declared-skills' in {i.rule_id for i in result['strengths']}
    assert all(i.finding_ids[0] in {t.id for t in threats} for i in result['threats'])
    assert all(t.severity_reason for t in threats if t.severity)


def test_zero_and_stale_no_unsupported_opportunity():
    c=context(distances=(),related=0)
    competition=analyze_competition(c)
    swot=analyze_swot(c,competition,analyze_threats(c,competition))
    assert swot['opportunities']==[]
    assert not any('competition' in i.rule_id for i in swot['strengths'])
    c=context(stale=True)
    competition=analyze_competition(c)
    assert analyze_swot(c,competition,analyze_threats(c,competition))['opportunities']==[]
    assert not any(t.rule_id=='mapped-pressure' for t in analyze_threats(c,competition))


def assumptions(**overrides):
    item=dict(name='Explicit test service', unit='job', variable_unit_cost='40', monthly_volume='100', allocated_monthly_fixed_cost='1000', overhead_weight='1', target_margin_range=['0.2','0.2'], source='test planning assumption', version='test-v1')
    item.update(overrides)
    return PricingAssumptions(items=[PricingItem(**item)], monthly_fixed_cost='1000')


def test_pricing_margin_not_markup():
    result=analyze_pricing(assumptions())
    item=result['items'][0]
    assert item['planning_cost_per_unit']=='50.00'
    assert item['recommended_target']=='62.50'  # Not 60.00 markup.
    assert item['unit_contribution']=='22.50'
    assert Decimal(item['operating_break_even_volume']) == Decimal('1000') / Decimal('22.50')
    assert result['purchasing_power_adjustment'] is result['competitor_price_adjustment'] is None


@pytest.mark.parametrize('volume', ['0','-1'])
def test_invalid_volume_returns_no_price(volume):
    assert analyze_pricing(assumptions(monthly_volume=volume))['items']==[]


@pytest.mark.parametrize('margins', [['1','1'],['-0.1','0.2'],['0.5','0.2']])
def test_invalid_margin_returns_no_price(margins):
    assert analyze_pricing(assumptions(target_margin_range=margins))['items']==[]


def test_multi_item_allocation():
    a=assumptions(allocated_monthly_fixed_cost='500',overhead_weight='0.5')
    second=a.items[0].model_copy(update={'name':'Second', 'unit':'litre'})
    a.items.append(second)
    result=analyze_pricing(a)
    assert len(result['items'])==2 and result['aggregate_break_even'] is None
    a.items[0].overhead_weight=Decimal('1')
    assert analyze_pricing(a)['items']==[]


def test_missing_assumptions_and_rounding():
    empty=analyze_pricing(PricingAssumptions())
    assert empty['items']==[] and empty['missing_assumptions']
    assert empty['demographic_status']=='VERIFIED_DATA_UNAVAILABLE'
    assert empty['local_price_status']=='LOCAL_PRICE_DATA_UNAVAILABLE'
    assert empty['purchasing_power_status']=='PURCHASING_POWER_DATA_UNAVAILABLE'
    result=analyze_pricing(assumptions(variable_unit_cost='40.005',target_margin_range=['0','0']))
    assert result['items'][0]['recommended_target']=='50.01'


def test_nonpositive_contribution_no_break_even():
    a=assumptions(variable_unit_cost='0',allocated_monthly_fixed_cost='0',target_margin_range=['0','0'])
    a.monthly_fixed_cost=Decimal('0')
    assert analyze_pricing(a)['items'][0]['operating_break_even_volume'] is None


def test_engines_deterministic_and_read_only():
    c=context()
    before=deepcopy(c)
    first=analyze_competition(c)
    assert first==analyze_competition(c)
    assert [t.model_dump() for t in analyze_threats(c,first)]==[t.model_dump() for t in analyze_threats(c,first)]
    assert c==before
