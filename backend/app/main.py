from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_v1_router
from app.config import settings
from app.db.session import engine
from app.middleware.locale import LocaleMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Travel-AI",
        description="Intelligent travel aggregation platform",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(LocaleMiddleware)

    app.include_router(api_v1_router, prefix="/api/v1")

    if settings.ADMIN_ENABLED:
        from app.admin import setup_admin

        setup_admin(app, engine)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
