"""APScheduler daily job: fetch RSS → DeepSeek analyze → save cards."""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.services.rss_fetcher import fetch_and_store, get_today_all_items, mark_analyzed
from backend.services.clustering import cluster_items, get_related_groups, get_crossdomain_groups
from backend.services.deepseek_analyzer import analyze_items, analyze_items_crossdomain
from backend.services.opportunity_store import save_cards

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def run_generation_once() -> dict:
    """Fetch RSS → cluster → analyze related + cross-domain → save cards."""
    # --- Step 1: Fetch all RSS items (incremental save) ---
    logger.info("Step 1: Fetching RSS feed…")
    fetch_and_store()

    # --- Step 2: Get today's items ---
    logger.info("Step 2: Loading today's items…")
    today_items = get_today_all_items()
    if not today_items:
        logger.info("No items found for today — skipping generation")
        return {"message": "No items for today", "cards": []}
    logger.info(f"Found {len(today_items)} items for today")

    # --- Step 3: Cluster by topic ---
    logger.info("Step 3: Clustering items by topic…")
    clustered = cluster_items(today_items)
    logger.info(f"Formed {len(clustered)} clusters: {list(clustered.keys())}")

    all_cards: list[dict] = []

    # --- Step 4-5: Related analysis ---
    logger.info("Step 4: Selecting related groups…")
    related_groups = get_related_groups(clustered, n_groups=3, items_per_group=3)
    logger.info(f"Selected {len(related_groups)} related groups")

    for i, group in enumerate(related_groups):
        logger.info(f"Step 5: Analyzing related group {i+1}/{len(related_groups)} ({len(group)} items)…")
        try:
            cards = analyze_items(group, card_type="related")
            if cards:
                all_cards.extend(cards)
                logger.info(f"  → Generated {len(cards)} related cards")
            else:
                logger.info(f"  → No cards from related group {i+1}")
        except Exception as e:
            logger.error(f"  → Related group {i+1} failed: {e}")

    # --- Step 6-7: Cross-domain analysis ---
    logger.info("Step 6: Selecting cross-domain groups…")
    cross_groups = get_crossdomain_groups(clustered, n_groups=3, items_per_group=3)
    logger.info(f"Selected {len(cross_groups)} cross-domain groups")

    for i, group in enumerate(cross_groups):
        logger.info(f"Step 7: Analyzing cross-domain group {i+1}/{len(cross_groups)} ({len(group)} items)…")
        try:
            cards = analyze_items_crossdomain(group, card_type="crossdomain")
            if cards:
                all_cards.extend(cards)
                logger.info(f"  → Generated {len(cards)} cross-domain cards")
            else:
                logger.info(f"  → No cards from cross-domain group {i+1}")
        except Exception as e:
            logger.error(f"  → Cross-domain group {i+1} failed: {e}")

    # --- Step 8: Save all cards ---
    if all_cards:
        save_cards(all_cards)
        logger.info(f"Step 8: Saved {len(all_cards)} total cards")
    else:
        logger.info("Step 8: No cards generated from any group")

    # --- Step 9: Mark items as analyzed ---
    analyzed_ids = [item["id"] for item in today_items]
    mark_analyzed(analyzed_ids)
    logger.info(f"Step 9: Marked {len(analyzed_ids)} items as analyzed")

    logger.info(f"Done — generated {len(all_cards)} cards total")
    return {"message": f"Generated {len(all_cards)} cards", "cards": all_cards}


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
        trigger=CronTrigger(hour=8, minute=30, timezone='Asia/Shanghai'),
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
        _scheduler.shutdown(wait=True)
        _scheduler = None
        logger.info("Scheduler stopped")
