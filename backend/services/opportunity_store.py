"""CRUD operations for opportunity cards."""

import json
from datetime import date
from backend.models import get_db
from backend.services.kickoff import build_kickoff_prompt


def save_cards(cards: list[dict]) -> list[int]:
    """Save opportunity cards to database, return list of inserted IDs."""
    conn = get_db()
    ids = []
    for card in cards:
        # Serialize source arrays to JSON strings
        source_titles_json = json.dumps(card.get("source_titles", []), ensure_ascii=False) if card.get("source_titles") else None
        source_urls_json = json.dumps(card.get("source_urls", []), ensure_ascii=False) if card.get("source_urls") else None
        kickoff_json = json.dumps(card["kickoff"], ensure_ascii=False) if card.get("kickoff") else None
        kickoff_prompt = card.get("kickoff_prompt") or build_kickoff_prompt(card)

        cur = conn.execute(
            "INSERT INTO opportunity_cards "
            "(title, user_persona, pain_point, ai_solution, mvp_plan, score, risks, next_step, source_title, source_url, source_titles, source_urls, direction, card_type, kickoff, kickoff_prompt) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                card["title"],
                card["user_persona"],
                card["pain_point"],
                card["ai_solution"],
                card["mvp_plan"],
                json.dumps(card["score"], ensure_ascii=False),
                card["risks"],
                card["next_step"],
                card.get("source_title", ""),
                card.get("source_url", ""),
                source_titles_json,
                source_urls_json,
                card.get("direction", ""),
                card.get("card_type", "related"),
                kickoff_json,
                kickoff_prompt,
            ),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    conn.close()
    return ids


def get_today_cards() -> list[dict]:
    """Get today's opportunity cards."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM opportunity_cards WHERE created_at = ? ORDER BY id",
        (date.today().isoformat(),),
    ).fetchall()
    conn.close()
    return [_row_to_card(r) for r in rows]


def get_latest_cards() -> tuple[list[dict], str]:
    """Get today's cards; fall back to the most recent day that has cards.

    Returns (cards, actual_date_iso).
    """
    today_iso = date.today().isoformat()
    cards = get_today_cards()
    if cards:
        return cards, today_iso

    # Find the most recent date that has cards
    conn = get_db()
    row = conn.execute(
        "SELECT created_at FROM opportunity_cards ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if not row:
        conn.close()
        return [], today_iso

    latest_date = row["created_at"]
    rows = conn.execute(
        "SELECT * FROM opportunity_cards WHERE created_at = ? ORDER BY id",
        (latest_date,),
    ).fetchall()
    conn.close()
    cards = [_row_to_card(r) for r in rows]
    return cards, latest_date


def get_card_by_id(card_id: int) -> dict | None:
    """Get a single card by ID."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM opportunity_cards WHERE id = ?", (card_id,)
    ).fetchone()
    conn.close()
    if row:
        return _row_to_card(row)
    return None


def get_all_cards(keyword: str = "", direction: str = "", date_filter: str = "",
                  page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
    """Get cards with optional filters and pagination. Returns (cards, total)."""
    conn = get_db()
    where = "WHERE 1=1"
    params: list = []

    if keyword:
        like = f"%{keyword}%"
        where += " AND (title LIKE ? OR pain_point LIKE ? OR ai_solution LIKE ? OR user_persona LIKE ?)"
        params.extend([like, like, like, like])

    if direction:
        where += " AND direction = ?"
        params.append(direction)

    if date_filter:
        where += " AND created_at = ?"
        params.append(date_filter)

    # Count total matching rows
    count_query = f"SELECT COUNT(*) FROM opportunity_cards {where}"
    total_row = conn.execute(count_query, params).fetchone()
    total = total_row[0] if total_row else 0

    # Fetch page
    offset = (page - 1) * page_size
    query = f"SELECT * FROM opportunity_cards {where} ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?"
    rows = conn.execute(query, params + [page_size, offset]).fetchall()
    conn.close()
    return [_card_light(r) for r in rows], total


def _card_light(row) -> dict:
    """Serialize a database row to a light card dict for list endpoints.

    Only returns fields needed by the library list view:
    id, title, direction, card_type, score, created_at, source_title.
    """
    d = dict(row)
    score = d.get("score")
    if isinstance(score, str):
        try:
            score = json.loads(score)
        except (json.JSONDecodeError, TypeError):
            score = 0
    if isinstance(score, dict):
        score = score.get("total", 0)
    elif not isinstance(score, (int, float)):
        score = 0
    return {
        "id": d["id"],
        "title": d["title"],
        "direction": d.get("direction", ""),
        "card_type": d.get("card_type", "related"),
        "score": score,
        "created_at": d.get("created_at", ""),
        "source_title": d.get("source_title", ""),
    }


def _row_to_card(row) -> dict:
    """Convert a database row to a card dict."""
    d = dict(row)
    if isinstance(d.get("score"), str):
        d["score"] = json.loads(d["score"])
    for key in ("source_titles", "source_urls", "kickoff"):
        if isinstance(d.get(key), str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                d[key] = {} if key == "kickoff" else []
    # Backward compat: old cards without a stored prompt get one composed on the fly
    if not d.get("kickoff_prompt"):
        d["kickoff_prompt"] = build_kickoff_prompt(d)
    return d
