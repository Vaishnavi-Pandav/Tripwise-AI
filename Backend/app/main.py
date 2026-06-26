import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import app.models  # noqa: F401
from app.api import (
    admin, ai, analytics, attractions, auth,
    budget, comparison, export, favorites, hotels, itinerary,
    notifications, optimizer, packages, routes,
    saved_trips, search, settings_router, trips, weather,
)
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.rate_limit import limiter
from app.db.session import Base, engine
from app.middleware.logging import RequestLoggingMiddleware

logging.basicConfig(level=logging.INFO)
if os.getenv("RUN_MIGRATIONS", "false").lower() == "true":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Auth",                   "description": "Signup, login, profile"},
        {"name": "Trips",                  "description": "Trip CRUD"},
        {"name": "Budget",                 "description": "Budget breakdown & optimizer"},
        {"name": "AI Budget Optimizer",    "description": "AI cost-saving recommendations"},
        {"name": "Hotels",                 "description": "Hotel listing & recommendations"},
        {"name": "Packages",               "description": "Travel packages"},
        {"name": "Itinerary",              "description": "AI-generated itineraries"},
        {"name": "Attractions & Hidden Gems","description": "Attractions & hidden gems"},
        {"name": "Destination Comparison", "description": "Compare destinations"},
        {"name": "Weather",                "description": "Weather info & advisory"},
        {"name": "AI Assistant",           "description": "AI travel chat assistant"},
        {"name": "Routes & Maps",          "description": "Route planning & nearby attractions"},
        {"name": "Saved Trips",            "description": "Save/unsave trips"},
        {"name": "Favorites & Wishlist",   "description": "Save hotels, destinations, packages"},
        {"name": "Notifications",          "description": "Travel alerts & reminders"},
        {"name": "Analytics Dashboard",    "description": "Travel analytics & stats"},
        {"name": "Global Search",          "description": "Search across all entities"},
        {"name": "User Settings",          "description": "Preferences & settings"},
        {"name": "PDF Export",             "description": "Export trip data"},
        {"name": "Admin",                  "description": "Admin management panel"},
    ],
)

# ── CORS must be FIRST before any other middleware ────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        settings.FRONTEND_URL,
        "https://tripwise-ai.vercel.app", # your production Vercel URL
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
register_exception_handlers(app)

PREFIX = "/api/v1"
app.include_router(auth.router,            prefix=PREFIX)
app.include_router(trips.router,           prefix=PREFIX)
app.include_router(budget.router,          prefix=PREFIX)
app.include_router(optimizer.router,       prefix=PREFIX)
app.include_router(hotels.router,          prefix=PREFIX)
app.include_router(packages.router,        prefix=PREFIX)
app.include_router(itinerary.router,       prefix=PREFIX)
app.include_router(attractions.router,     prefix=PREFIX)
app.include_router(comparison.router,      prefix=PREFIX)
app.include_router(weather.router,         prefix=PREFIX)
app.include_router(ai.router,              prefix=PREFIX)
app.include_router(routes.router,          prefix=PREFIX)
app.include_router(saved_trips.router,     prefix=PREFIX)
app.include_router(favorites.router,       prefix=PREFIX)
app.include_router(notifications.router,   prefix=PREFIX)
app.include_router(analytics.router,       prefix=PREFIX)
app.include_router(search.router,          prefix=PREFIX)
app.include_router(settings_router.router, prefix=PREFIX)
app.include_router(export.router,          prefix=PREFIX)
app.include_router(admin.router,           prefix=PREFIX)

@app.get("/", tags=["Health"])
def root():
    return {"app": settings.APP_NAME, "version": settings.VERSION, "status": "running 🚀", "docs": "/docs"}
