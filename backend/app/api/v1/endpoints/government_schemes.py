from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.government_scheme import (
    DISCOVERY_DISCLAIMER, GovernmentSchemeDetail, GovernmentSchemeFilters,
    GovernmentSchemePage, GovernmentSchemeQuery,
)
from app.services.government_scheme_service import GovernmentSchemeService

router = APIRouter()


@router.get('', response_model=GovernmentSchemePage, summary='Browse active government schemes',
            description=DISCOVERY_DISCLAIMER + ' Public, read-only catalog. Filters combine with AND. Pagination defaults to 20, maximum 100. Search uses English full-text relevance before the selected sort; slug breaks ties. No personalized matching.')
def list_government_schemes(db: Annotated[Session, Depends(get_db)], filters: Annotated[GovernmentSchemeQuery, Query()]):
    return GovernmentSchemeService(db).list(filters)


# Register the static route before /{slug}.
@router.get('/filters', response_model=GovernmentSchemeFilters, summary='Available active catalog filters',
            description='Distinct, sorted values present in active catalog records. Categories are exact labels; no tags or inactive metadata are exposed.')
def government_scheme_filters(db: Annotated[Session, Depends(get_db)]):
    return GovernmentSchemeService(db).filters()


@router.get('/{slug}', response_model=GovernmentSchemeDetail, summary='Read an active government scheme',
            description=DISCOVERY_DISCLAIMER + ' Returns source prose and provenance. Unknown and inactive slugs return 404.',
            responses={404: {'description': 'Government scheme not found'}})
def get_government_scheme(db: Annotated[Session, Depends(get_db)], slug: Annotated[str, Path(min_length=1, max_length=120)]):
    return GovernmentSchemeService(db).get(slug)
