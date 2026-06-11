from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import trips

app = FastAPI(
    title="TripWise AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────
app.include_router(trips.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "TripWise AI is running 🚀"}
