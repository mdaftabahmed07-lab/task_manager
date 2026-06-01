from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.config.settings import settings
from app.database.session import Base, engine
from app.routes import auth, tasks
import app.models  # noqa: F401 — registers models with SQLAlchemy metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only run create_all if we haven't been told to skip it (e.g. during tests)
    if not getattr(app.state, "skip_create_all", False):
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A clean, production-ready Task Management API built with FastAPI and PostgreSQL. "
        "Register an account, log in to get your JWT token, then manage your tasks."
    ),
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — adjust origins before going to production
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global error handlers
# ---------------------------------------------------------------------------
@app.exception_handler(OperationalError)
async def db_connection_error_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database is unavailable. Please try again shortly."},
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
