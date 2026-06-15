"""Product LingLing — FastAPI backend."""

import logging
import os
from datetime import date
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.models import init_db
from backend.services.rss_fetcher import get_all_rss_items
from backend.services.opportunity_store import (
    get_today_cards,
    get_latest_cards,
    get_card_by_id,
    get_all_cards,
)
from backend.services.scheduler import start_scheduler, stop_scheduler, run_generation_once

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Product LingLing", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Cards ──

@app.get("/api/cards")
def list_cards(
    keyword: str = Query("", description="Search keyword"),
    direction: str = Query("", description="Filter by direction"),
    date: str = Query("", description="Filter by date (YYYY-MM-DD)"),
):
    """List all opportunity cards with optional filters."""
    cards = get_all_cards(keyword=keyword, direction=direction, date_filter=date)
    return {"cards": cards, "total": len(cards)}


@app.get("/api/cards/today")
def today_cards():
    """Return today's opportunity cards (read-only — generation is scheduled).

    Falls back to yesterday's cards when today has none yet.
    """
    cards, actual_date = get_latest_cards()
    today_iso = date.today().isoformat()
    return {"cards": cards, "generated": len(cards) > 0, "date": actual_date, "is_today": actual_date == today_iso}


@app.get("/api/cards/{card_id}")
def card_detail(card_id: int):
    """Get a single card by ID."""
    card = get_card_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@app.post("/api/cards/generate")
def generate_cards():
    """Manually trigger RSS fetch + DeepSeek analysis (dev only)."""
    if os.environ.get("LING_ENV", "") != "development":
        raise HTTPException(status_code=404, detail="Not found")
    # Prevent duplicate generation if today already has cards
    existing = get_today_cards()
    if existing:
        return {"message": f"Today already has {len(existing)} cards. Skip.", "cards": []}
    try:
        result = run_generation_once()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Generation failed: {e}")
    return result


# ── Sources ──

@app.get("/api/sources")
def list_sources():
    """Return all cached feed items from the information source."""
    items = get_all_rss_items()
    return {"items": items, "total": len(items)}
