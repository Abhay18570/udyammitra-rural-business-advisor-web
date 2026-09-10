import uuid
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException
from app.business_analysis_rules import BUSINESS_MITIGATIONS, RULE_VERSIONS
from app.engines.nearby_market_engine import fingerprint, normalize_location
from app.engines.financial_engine import align_business_cost
from app.engines.profile_evidence import match_requirements
from app.engines.competitor_analysis_engine import analyze_competition
from app.engines.threat_engine import analyze_threats
from app.engines.swot_engine import analyze_swot
from app.engines.pricing_engine import analyze_pricing
from app.models.business import BusinessProfile
from app.models.business_analysis import BusinessAnalysis
from app.repositories.financial_repository import FinancialRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.business_analysis_repository import BusinessAnalysisRepository
from app.schemas.business_analysis import BusinessAnalysisContext, BusinessAnalysisResponse, Evidence
from app.schemas.nearby_market import NearbyMarketRequest
from app.schemas.scheme import SchemeAnalysisRequest
from app.services.profile_service import ProfileService
from app.services.financial_service import FinancialService
from app.services.scheme_service import SchemeService
from app.services.nearby_market_service import NearbyMarketService


def conflict(code, message):
    raise HTTPException(status_code=409, detail={'code': code, 'message': message})


def catalog_snapshot(business):
    fields = ['slug', 'name', 'category', 'business_type', 'minimum_capital', 'maximum_capital',
        'estimated_setup_cost_min', 'estimated_setup_cost_max', 'working_capital_min', 'working_capital_max',
        'required_skills', 'preferred_skills', 'required_resources', 'optional_resources', 'equipment',
        'customer_segments', 'market_drivers', 'competition_factors', 'supply_chain_factors', 'major_risks',
        'required_registrations', 'operating_requirements', 'baseline_swot']
    def encode(value):
        return str(value) if isinstance(value, Decimal) else value.value if hasattr(value, 'value') else value
    return {field: encode(getattr(business, field)) for field in fields}


class BusinessAnalysisService:
    def __init__(self, db):
        self.db = db
        self.repository = BusinessAnalysisRepository(db)

    def sources(self, user, payload):
        row = FinancialRepository(self.db).get_owned(payload.financial_analysis_id, user.id)
        if row is None:
            raise HTTPException(status_code=404, detail='Financial analysis not found.')
        # Reuse existing money invariants and explicit financial-version validation.
        scheme = SchemeService(self.db).analyze(user, SchemeAnalysisRequest(financial_analysis_id=row.id))
        business = self.db.get(BusinessProfile, row.business_profile_id)
        if not business or not business.is_active or business.slug not in BUSINESS_MITIGATIONS:
            raise HTTPException(status_code=404, detail='Active supported business not found.')
        profile = ProfileRepository(self.db).get_for_user(user)
        if not profile or not all(getattr(profile, key) for key in ('village', 'taluka', 'district', 'state')):
            conflict('PROFILE_LOCATION_REQUIRED', 'Complete profile location before analysis.')
        if not profile.proposed_business_id:
            conflict('PROPOSED_BUSINESS_REQUIRED', 'Select a proposed business in Profile first.')
        if profile.proposed_business_id != business.id:
            conflict('PROPOSED_BUSINESS_MISMATCH', 'The financial analysis business differs from your proposed business. Select a matching financial plan.')
        try:
            financial = FinancialService(self.db)._response(row)
            if financial.business.slug != business.slug or financial.business.category != business.category.value:
                raise ValueError('Business identity changed')
            for field in ('minimum_capital', 'maximum_capital', 'estimated_setup_cost_min', 'estimated_setup_cost_max', 'working_capital_min', 'working_capital_max'):
                if Decimal(row.business_cost_snapshot[field]) != getattr(business, field):
                    conflict('CATALOG_COSTS_CHANGED', 'Catalog costs changed. Recalculate the financial plan.')
            alignment = align_business_cost(row.feasible_project_cost, business)
            if row.funding_gap != alignment['funding_gap'] or Decimal(financial.alignment.funding_gap) != alignment['funding_gap'] or financial.alignment.setup_cost_coverage_status != alignment['setup_cost_coverage_status'] or financial.alignment.financial_readiness_status != alignment['financial_readiness_status'] or Decimal(financial.alignment.capacity_above_estimated_max) != alignment['capacity_above_estimated_max']:
                raise ValueError('Inconsistent alignment')
        except (ValueError, KeyError, TypeError, ArithmeticError):
            conflict('INCONSISTENT_FINANCIAL_SNAPSHOT', 'Saved financial evidence is incompatible. Recalculate the financial plan.')
        # Include only analysis-relevant self-reports, not personal identity or age.
        raw = ProfileService(self.db)._response(user, profile).model_dump(mode='json')
        profile_data = {key: raw[key] for key in ['proposed_business_id', 'own_capital', 'skills', 'resources', 'has_existing_business', 'existing_business', 'state', 'district', 'taluka', 'village', 'pincode']}
        profile_data['observed_at'] = profile.updated_at.isoformat()
        catalog = catalog_snapshot(business)
        return business, profile_data, catalog, financial, scheme

    def analyze(self, user, payload):
        business, profile, catalog, financial, scheme = self.sources(user, payload)
        before = fingerprint({'profile': profile, 'catalog': catalog, 'financial': financial.model_dump(mode='json'), 'scheme': scheme.model_dump(mode='json')})
        business_id, slug = business.id, business.slug
        market = NearbyMarketService(self.db).analyze(user, NearbyMarketRequest(business_slug=slug, radius_km=payload.radius_km))
        if market.source.provider == 'GOOGLE_PLACES':
            conflict('GOOGLE_HISTORY_UNAVAILABLE', 'Google nearby evidence is live only. Saved business analysis is unavailable until policy-safe history is implemented.')
        if not market.quality.complete_query:
            conflict('MARKET_COVERAGE_INCOMPLETE', 'Complete real market evidence is required.')
        if market.business.id != business_id or market.radius.selected_km != payload.radius_km:
            conflict('MARKET_CONTEXT_MISMATCH', 'Market evidence does not match this analysis.')
        # Provider calls can take time; never save an analysis against silently changed sources.
        self.db.expire_all()
        business, current_profile, current_catalog, current_financial, current_scheme = self.sources(user, payload)
        after = fingerprint({'profile': current_profile, 'catalog': current_catalog, 'financial': current_financial.model_dump(mode='json'), 'scheme': current_scheme.model_dump(mode='json')})
        if before != after:
            conflict('ANALYSIS_CONTEXT_CHANGED', 'Profile or source assumptions changed during analysis. Retry with the current inputs.')
        own = Decimal(profile['own_capital']) if profile['own_capital'] is not None else None
        margin = Decimal(financial.available_margin_capital)
        budget = {'own_capital': own, 'financial_margin': margin, 'consistency_status': 'NOT_RECORDED' if own is None else 'CONSISTENT' if own == margin else 'DIFFERENT'}
        skills = [i['name'] for i in profile['skills']]
        resources = [i['name'] for i in profile['resources']]
        existing = profile['existing_business']
        # Free-text categories are not canonical IDs; exact catalog name/slug is the only accepted link.
        same_existing = existing and normalize_location(existing['business_category']) in {normalize_location(slug), normalize_location(business.name)}
        entrepreneur = {'enterprise_stage': 'EXISTING' if profile['has_existing_business'] else 'NEW' if profile['has_existing_business'] is False else 'UNKNOWN',
            'declared_skills': skills, 'declared_resources': resources,
            'skills': match_requirements(skills, catalog['required_skills'], 'skills'),
            'resources': match_requirements(resources, catalog['required_resources'], 'resources'),
            'existing_business_observations': {key: existing[key] for key in ('monthly_revenue', 'monthly_expenses', 'years_operating', 'estimated_monthly_customers')} if same_existing and profile['has_existing_business'] else None}
        versions = {**RULE_VERSIONS, 'financial': financial.analysis_version, 'scheme': scheme.scheme_rules_version, ('nearby_mapping' if market.source.provider == 'GOOGLE_PLACES' else 'osm_mapping'): market.source.mapping_version}
        evidence = []
        def add(key, value, source, reference, **kwargs):
            evidence.append(Evidence(id=key, value=value, source_kind=source, source_ref=reference, **kwargs))
        for kind in ('skills', 'resources'):
            add('profile.' + kind, [m.model_dump() for m in entrepreneur[kind]], 'SELF_REPORTED', 'current-profile', is_self_report=True, observed_at=profile['observed_at'], limitations=['Broad aliases are tentative; not independently verified.'])
        add('profile.budget', {key: str(value) if isinstance(value, Decimal) else value for key, value in budget.items()}, 'SELF_REPORTED', 'current-profile', unit='INR', is_self_report=True, observed_at=profile['observed_at'])
        if catalog.get('baseline_swot'):
            add('catalog.baseline_swot', catalog['baseline_swot'], 'BUSINESS_BASELINE', catalog['baseline_swot']['version'], is_assumption=True, limitations=['General business guidance, not verified local demand or observed competition.'])
        add('catalog.risks', catalog['major_risks'], 'CATALOG_ASSUMPTION', fingerprint(catalog), is_assumption=True)
        add('catalog.requirements', {key: catalog[key] for key in ('required_skills', 'required_resources', 'operating_requirements')}, 'CATALOG_ASSUMPTION', fingerprint(catalog), is_assumption=True)
        add('financial.setup', {'project_capacity': financial.feasible_project_cost, 'costs': financial.business_costs, 'alignment': financial.alignment.model_dump()}, 'CALCULATED', str(financial.id), observed_at=financial.created_at, unit='INR', is_assumption=True)
        add('financial.scheme', scheme.model_dump(mode='json'), 'CALCULATED', str(financial.id), observed_at=financial.created_at, is_assumption=True, limitations=[scheme.disclaimer])
        for kind, records in [('direct', market.competitors), ('related', market.related_businesses)]:
            add('market.' + kind, [p.model_dump(mode='json') for p in records], 'OBSERVED_LOCAL', market.source.provider,
                observed_at=market.source.fetched_at, geography=market.location.location_fingerprint, radius_km=payload.radius_km,
                limitations=['Mapped records are not a complete establishment census.'])
        add('market.quality', {'quality': market.quality.model_dump(mode='json'), 'source': market.source.model_dump(mode='json')}, 'DATA_LIMITATION', market.source.provider)
        add('pricing.assumptions', {'status': 'INSUFFICIENT_PRICING_ASSUMPTIONS', 'items': []}, 'DATA_LIMITATION', fingerprint(catalog))
        add('data.demographics', 'VERIFIED_DATA_UNAVAILABLE', 'DATA_LIMITATION', 'No verified demographic or purchasing-power dataset configured.')
        context = BusinessAnalysisContext(entrepreneur=entrepreneur,
            business={'id': business_id, 'slug': slug, 'name': business.name, 'category': business.category.value, 'business_type': business.business_type.value, 'catalog_hash': fingerprint(catalog), 'catalog_snapshot': catalog},
            financial=financial, scheme=scheme, budget=budget, profile_fingerprint=fingerprint(profile), market=market,
            evidence=evidence, rule_versions=versions, quality={'missing': ['pricing', 'demographics', 'purchasing_power'],
                'stale': ['market'] if market.source.cache_status == 'STALE_CACHE' else [],
                'conflicting': ['profile_capital_vs_financial_margin'] if own is not None and own != margin else [],
                'limited': [w.code for w in market.quality.warnings]})
        competition = analyze_competition(context)
        threats = analyze_threats(context, competition)
        pricing = analyze_pricing(context.pricing_assumptions)
        swot = analyze_swot(context, competition, threats)
        context_hash = fingerprint(context.model_dump(mode='json'))
        response = BusinessAnalysisResponse(id=uuid.uuid4(), created_at=datetime.now(timezone.utc), business=context.business,
            profile_context=context.entrepreneur, financial_context={'analysis': financial.model_dump(mode='json'), 'scheme': scheme.model_dump(mode='json'), 'budget': context.budget.model_dump(mode='json')},
            market_context=market, swot=swot, local_threats=threats, competition=competition, pricing=pricing, evidence=evidence,
            quality={'section_statuses': {'swot': 'BASELINE_AND_EVIDENCE' if catalog.get('baseline_swot') else 'EVIDENCE_BASED', 'threats': 'EVIDENCE_BASED', 'competition': competition['classification'], 'pricing': pricing['status']},
                'sources': ['SELF_REPORTED_PROFILE', 'CATALOG_ASSUMPTIONS', 'FINANCIAL_SNAPSHOT', 'PROTOTYPE_SCHEME_RULES', 'GOOGLE_PLACES' if market.source.provider == 'GOOGLE_PLACES' else 'OPENSTREETMAP'],
                'freshness': market.source.model_dump(mode='json'), 'warnings': context.quality,
                'rule_versions': versions, 'context_hash': context_hash})
        self.repository.save(BusinessAnalysis(id=response.id, user_id=user.id, business_id=business_id, financial_analysis_id=financial.id,
            created_at=response.created_at, selected_radius=payload.radius_km, profile_fingerprint=context.profile_fingerprint,
            location_fingerprint=market.location.location_fingerprint, rule_versions=versions, catalog_hash=context.business.catalog_hash,
            context_hash=context_hash, evidence_snapshot=context.model_dump(mode='json'), result_snapshot=response.model_dump(mode='json')))
        return response

    def get(self, user, analysis_id):
        row = self.repository.get_owned(analysis_id, user.id)
        if row is None:
            raise HTTPException(status_code=404, detail='Business analysis not found.')
        return BusinessAnalysisResponse.model_validate(row.result_snapshot)
