from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.profile import router as profile_router
from app.api.v1.endpoints.businesses import router as business_router
from app.api.v1.endpoints.market import router as market_router
from app.api.v1.endpoints.feasibility import router as feasibility_router
from app.api.v1.endpoints.financial import router as financial_router
from app.api.v1.endpoints.schemes import router as scheme_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(auth_router, prefix="/auth", tags=["authentication"])
router.include_router(profile_router, prefix="/profile", tags=["entrepreneur profile"])
router.include_router(business_router, prefix="/businesses", tags=["business catalog"])
router.include_router(market_router, prefix="/market", tags=["hyper-local market intelligence"])
router.include_router(feasibility_router, prefix="/feasibility", tags=["business feasibility"])
router.include_router(financial_router, prefix="/financial", tags=["financial calculator"])

router.include_router(scheme_router, prefix="/schemes", tags=["scheme eligibility guidance"])

from app.api.v1.endpoints.business_analysis import router as business_analysis_router
router.include_router(business_analysis_router, prefix='/business-analysis', tags=['business analysis'])
