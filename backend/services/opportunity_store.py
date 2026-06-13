"""CRUD operations for opportunity cards."""

import json
from datetime import date
from backend.models import get_db


def save_cards(cards: list[dict]) -> list[int]:
    """Save opportunity cards to database, return list of inserted IDs."""
    conn = get_db()
    ids = []
    for card in cards:
        cur = conn.execute(
            "INSERT INTO opportunity_cards "
            "(title, user_persona, pain_point, ai_solution, mvp_plan, score, risks, next_step, source_title, source_url, direction) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                card.get("direction", ""),
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


def get_all_cards(keyword: str = "", direction: str = "", date_filter: str = "") -> list[dict]:
    """Get all cards with optional keyword search, direction filter, and date filter."""
    conn = get_db()
    query = "SELECT * FROM opportunity_cards WHERE 1=1"
    params: list = []

    if keyword:
        like = f"%{keyword}%"
        query += " AND (title LIKE ? OR pain_point LIKE ? OR ai_solution LIKE ? OR user_persona LIKE ?)"
        params.extend([like, like, like, like])

    if direction:
        query += " AND direction = ?"
        params.append(direction)

    if date_filter:
        query += " AND created_at = ?"
        params.append(date_filter)

    query += " ORDER BY created_at DESC, id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_card(r) for r in rows]


def _row_to_card(row) -> dict:
    """Convert a database row to a card dict."""
    d = dict(row)
    if isinstance(d.get("score"), str):
        d["score"] = json.loads(d["score"])
    return d
