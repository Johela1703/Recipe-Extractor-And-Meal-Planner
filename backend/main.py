from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.database import engine
from backend.models import Base
from backend.routers import recipes, meal_planner
from backend.config import settings

# ─── Create all DB tables on startup ────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Recipe Extractor & Meal Planner API",
    description="Scrape recipe blog URLs, extract structured data with OpenRouter LLM...",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(recipes.router)
app.include_router(meal_planner.router)

# ─── Serve Frontend ───────────────────────────────────────────────────────────
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(str(FRONTEND_DIR / "index.html"))


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "Recipe Extractor API"}
