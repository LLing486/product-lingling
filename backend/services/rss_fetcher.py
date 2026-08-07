"""Fetch RSS items from AI HOT and store new entries."""

import logging
import feedparser
from backend.models import get_db

logger = logging.getLogger(__name__)

FEED_URL = "https://aihot.virxact.com/feed.xml"


def fetch_and_store() -> list[dict]:
    """Fetch RSS feed, insert new items (skip duplicates), return unanalyzed items."""
    feed = feedparser.parse(FEED_URL)

    if feed.bozo and not feed.entries:
        raise RuntimeError(f"RSS fetch failed: {feed.bozo_exception}")

    conn = get_db()
    inserted = 0

    for entry in feed.entries:
        url = entry.get("link", "")
        if not url:
            continue
        try:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO rss_items (title, url, description, published_at) VALUES (?, ?, ?, ?)",
                (
                    entry.get("title", ""),
                    url,
                    entry.get("summary", ""),
                    entry.get("published", ""),
                ),
            )
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            logger.warning(f"Failed to insert RSS item '{url[:60]}': {e}")
            continue

    conn.commit()

    # Return today's unanalyzed items only (prevent stale accumulation)
    rows = conn.execute(
        "SELECT id, title, url, description, published_at, fetched_at, is_analyzed "
        "FROM rss_items WHERE is_analyzed = 0 AND date(fetched_at) = date('now', 'localtime') "
        "ORDER BY id"
    ).fetchall()
    conn.close()

    return [dict(r) for r in rows]


def get_today_all_items() -> list[dict]:
    """Return ALL of today's fetched RSS items (analyzed or not), for clustering."""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, title, url, description, published_at, fetched_at, is_analyzed "
        "FROM rss_items WHERE date(fetched_at) = date('now', 'localtime') "
        "ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_today_unanalyzed_items() -> list[dict]:
    """Return today's unanalyzed RSS items."""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, title, url, description, published_at, fetched_at, is_analyzed "
        "FROM rss_items WHERE is_analyzed = 0 AND date(fetched_at) = date('now', 'localtime') "
        "ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_rss_items(limit: int = 50) -> list[dict]:
    """Return RSS items, limited to the most recent entries."""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, title, url, description, published_at, fetched_at, is_analyzed "
        "FROM rss_items ORDER BY fetched_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_analyzed(item_ids: list[int]):
    """Mark RSS items as analyzed."""
    if not item_ids:
        return
    conn = get_db()
    placeholders = ",".join("?" for _ in item_ids)
    conn.execute(
        f"UPDATE rss_items SET is_analyzed = 1 WHERE id IN ({placeholders})",
        item_ids,
    )
    conn.commit()
    conn.close()
