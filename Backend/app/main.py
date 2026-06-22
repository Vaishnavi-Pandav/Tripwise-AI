import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401 — registers all models with SQLAlchemy metadata
from app.api import (
    admin, ai, attractions, auth,
    budget, comparison, hotels, itinerary,
    packages, routes, saved_trips, trips, weather,
)
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.session import Base, engine
from app.middleware.logging import RequestLoggingMiddleware

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)

# ── Create DB tables ──────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Auth",                    "description": "Signup, login, profile"},
        {"name": "Trips",                   "description": "Trip CRUD"},
        {"name": "Budget",                  "description": "Budget breakdown calculator"},
        {"name": "Hotels",                  "description": "Hotel listing & recommendations"},
        {"name": "Packages",                "description": "Travel packages"},
        {"name": "Itinerary",               "description": "AI-generated itineraries"},
        {"name": "Attractions",             "description": "Attractions & hidden gems"},
        {"name": "Destination Comparison",  "description": "Compare two destinations"},
        {"name": "Weather",                 "description": "Weather info by city"},
        {"name": "AI Assistant",            "description": "AI travel chat assistant"},
        {"name": "Routes & Maps",           "description": "Route planning & nearby attractions"},
        {"name": "Saved Trips",             "description": "Save / unsave trips"},
        {"name": "Admin",                   "description": "Admin-only management endpoints"},
    ],
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(auth.router,        prefix=PREFIX)
app.include_router(trips.router,       prefix=PREFIX)
app.include_router(budget.router,      prefix=PREFIX)
app.include_router(hotels.router,      prefix=PREFIX)
app.include_router(packages.router,    prefix=PREFIX)
app.include_router(itinerary.router,   prefix=PREFIX)
app.include_router(attractions.router, prefix=PREFIX)
app.include_router(comparison.router,  prefix=PREFIX)
app.include_router(weather.router,     prefix=PREFIX)
app.include_router(ai.router,          prefix=PREFIX)
app.include_router(routes.router,      prefix=PREFIX)
app.include_router(saved_trips.router, prefix=PREFIX)
app.include_router(admin.router,       prefix=PREFIX)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running 🚀",
        "docs": "/docs",
    }
