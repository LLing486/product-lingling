"""Product LingLing — FastAPI backend."""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.models import init_db
from backend.services.rss_fetcher import fetch_and_store, get_all_rss_items
from backend.services.deepseek_analyzer import analyze_items
from backend.services.opportunity_store import (
    save_cards,
    get_today_cards,
    get_card_by_id,
    get_all_cards,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


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


@app.get("/api/today")
def today():
    """Return today's 4 opportunity cards. Generate them if they don't exist yet."""
    cards = get_today_cards()
    if cards:
        return {"cards": cards, "generated": False}

    # Auto-generate: fetch RSS → analyze → save
    try:
        unanalyzed = fetch_and_store()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"RSS fetch failed: {e}")

    if not unanalyzed:
        return {"cards": [], "generated": False, "message": "No new RSS items to analyze"}

    try:
        new_cards = analyze_items(unanalyzed)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"DeepSeek analysis failed: {e}")

    if new_cards:
        save_cards(new_cards)
        from backend.services.rss_fetcher import mark_analyzed
        mark_analyzed([item["id"] for item in unanalyzed])

    cards = get_today_cards()
    return {"cards": cards, "generated": True}


@app.get("/api/cards")
def list_cards(
    keyword: str = Query("", description="Search keyword"),
    direction: str = Query("", description="Filter by direction"),
):
    """List all opportunity cards with optional filters."""
    cards = get_all_cards(keyword=keyword, direction=direction)
    return {"cards": cards, "total": len(cards)}


@app.get("/api/cards/{card_id}")
def card_detail(card_id: int):
    """Get a single card by ID."""
    card = get_card_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@app.post("/api/generate")
def generate():
    """Manually trigger RSS fetch + DeepSeek analysis."""
    try:
        unanalyzed = fetch_and_store()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"RSS fetch failed: {e}")

    if not unanalyzed:
        return {"message": "No new RSS items to analyze", "cards": []}

    try:
        new_cards = analyze_items(unanalyzed)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"DeepSeek analysis failed: {e}")

    saved_ids = []
    if new_cards:
        saved_ids = save_cards(new_cards)
        from backend.services.rss_fetcher import mark_analyzed
        mark_analyzed([item["id"] for item in unanalyzed])

    return {
        "message": f"Generated {len(new_cards)} cards",
        "cards": get_all_cards()[: len(new_cards)],
    }


@app.get("/api/rss")
def rss_list():
    """Return all raw RSS items."""
    items = get_all_rss_items()
    return {"items": items, "total": len(items)}
