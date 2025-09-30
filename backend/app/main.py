from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from .routes.auth import router as auth_router
from .routes.persons import router as persons_router
from .routes.salaries import router as salaries_router
from .routes.stats import router as stats_router
from ..config import CORS_ORIGINS, DB_PATH


def create_app() -> FastAPI:
    app = FastAPI(title="Salary Manager", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(persons_router, prefix="/api/persons", tags=["persons"])
    app.include_router(salaries_router, prefix="/api/salaries", tags=["salaries"])
    app.include_router(stats_router, prefix="/api/stats", tags=["stats"])

    register_tortoise(
        app,
        db_url=f"sqlite://{DB_PATH}",
        modules={"models": ["backend.app.models.user", "backend.app.models.person", "backend.app.models.salary_record"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )

    return app


app = create_app()