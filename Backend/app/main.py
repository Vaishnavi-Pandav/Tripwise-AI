from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.api import ai, auth, hotels, packages, trips
import app.models  # noqa: F401 — registers all models with SQLAlchemy metadata

# Create all DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────
app.include_router(ai.router)
app.include_router(auth.router)
app.include_router(hotels.router)
app.include_router(packages.router)
app.include_router(trips.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": f"{settings.APP_NAME} v{settings.VERSION} is running 🚀"}
