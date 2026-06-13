"""APScheduler daily job: fetch RSS → DeepSeek analyze → save cards."""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.services.rss_fetcher import fetch_and_store, mark_analyzed
from backend.services.deepseek_analyzer import analyze_items
from backend.services.opportunity_store import save_cards

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def run_generation_once() -> dict:
    """Fetch RSS, analyze with DeepSeek, save cards. Returns a result dict."""
    logger.info("Fetching RSS feed…")
    unanalyzed = fetch_and_store()

    if not unanalyzed:
        logger.info("No new RSS items to analyze")
        return {"message": "No new RSS items to analyze", "cards": []}

    logger.info(f"Analyzing {len(unanalyzed)} unanalyzed items…")
    cards = analyze_items(unanalyzed)

    if cards:
        save_cards(cards)
        mark_analyzed([item["id"] for item in unanalyzed])
        logger.info(f"Generated {len(cards)} opportunity cards")
    else:
        logger.info("No cards generated")

    return {"message": f"Generated {len(cards)} cards", "cards": cards}


def _daily_job():
    """Wrapper for scheduler — logs errors instead of throwing."""
    try:
        run_generation_once()
    except Exception as e:
        logger.error(f"Scheduled generation failed: {e}")


def start_scheduler():
    """Start the background scheduler with a daily 08:30 trigger."""
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(
        _daily_job,
        trigger=CronTrigger(hour=8, minute=30),
        id="daily_opportunity_gen",
        name="Daily opportunity card generation",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started — daily job at 08:30")


def stop_scheduler():
    """Shut down the scheduler gracefully."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
