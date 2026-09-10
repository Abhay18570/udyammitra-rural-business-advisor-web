from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.db.session import get_db
from app.schemas.admin import AdminOverview
from app.services.admin_service import AdminService

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get('/overview', response_model=AdminOverview)
def overview(db: Annotated[Session, Depends(get_db)]) -> AdminOverview:
    return AdminService(db).overview()


from fastapi import Query, Response
from app.schemas.admin import StateAnalytics, DistrictAnalytics, EntrepreneurFilters, EntrepreneurPage


@router.get('/analytics/states', response_model=StateAnalytics)
def states(db: Annotated[Session, Depends(get_db)]) -> StateAnalytics:
    return AdminService(db).states()


@router.get('/analytics/states/{state:path}/districts', response_model=DistrictAnalytics)
def districts(state: str, db: Annotated[Session, Depends(get_db)]) -> DistrictAnalytics:
    return AdminService(db).districts(state)


@router.get('/entrepreneurs', response_model=EntrepreneurPage)
def entrepreneurs(filters: Annotated[EntrepreneurFilters, Query()], db: Annotated[Session, Depends(get_db)], response: Response) -> EntrepreneurPage:
    response.headers['Cache-Control'] = 'no-store'
    return AdminService(db).entrepreneurs(filters)
