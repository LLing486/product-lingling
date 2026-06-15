import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "lingling.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS opportunity_cards (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT NOT NULL,
            user_persona    TEXT NOT NULL,
            pain_point      TEXT NOT NULL,
            ai_solution     TEXT NOT NULL,
            mvp_plan        TEXT NOT NULL,
            score           TEXT NOT NULL,
            risks           TEXT NOT NULL,
            next_step       TEXT NOT NULL,
            source_title    TEXT,
            source_url      TEXT,
            direction       TEXT,
            card_type       TEXT NOT NULL DEFAULT 'related',
            created_at      TEXT NOT NULL DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS rss_items (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT NOT NULL,
            url             TEXT NOT NULL UNIQUE,
            description     TEXT,
            published_at    TEXT,
            fetched_at      TEXT NOT NULL DEFAULT (datetime('now')),
            is_analyzed     INTEGER NOT NULL DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_opportunity_cards_created_at
            ON opportunity_cards(created_at);
        CREATE INDEX IF NOT EXISTS idx_opportunity_cards_direction
            ON opportunity_cards(direction);
        CREATE INDEX IF NOT EXISTS idx_rss_items_is_analyzed
            ON rss_items(is_analyzed);
    """)
    conn.commit()

    # Migration: add card_type column if table exists without it
    cursor = conn.execute("PRAGMA table_info(opportunity_cards)")
    columns = [row[1] for row in cursor.fetchall()]
    if "card_type" not in columns:
        conn.execute("ALTER TABLE opportunity_cards ADD COLUMN card_type TEXT NOT NULL DEFAULT 'related'")
        conn.commit()

    conn.close()
