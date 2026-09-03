# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Request
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        description="Decision-support API for the UdyamMitra platform.",
        version="0.1.0",
        debug=settings.debug,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    cors_origins = [
        str(settings.frontend_url).rstrip("/"),
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    unique_origins = list(dict.fromkeys(cors_origins))

    application.add_middleware(
        CORSMiddleware,
        allow_origins=unique_origins,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$" if settings.app_env in {"development", "testing"} else None,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/", tags=["system"])
    def root() -> dict[str, str]:
        return {"name": settings.app_name, "status": "running", "api_version": "v1"}

    @application.exception_handler(Exception)
    async def unexpected_error_handler(_request: Request, _exception: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": "An unexpected server error occurred."})

    return application


app = create_app()
