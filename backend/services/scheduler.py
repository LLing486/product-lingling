"""APScheduler daily job: fetch RSS → cluster → analyze → save 1+1 cards."""

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
    """Fetch RSS → cluster → 1 related + 1 cross-domain card."""
    # Step 1: Fetch
    logger.info("Step 1: Fetching RSS feed…")
    fetch_and_store()

    # Step 2: Load today's items
    logger.info("Step 2: Loading today's items…")
    today_items = get_today_all_items()
    if not today_items:
        logger.info("No items for today — skipping")
        return {"message": "No items for today", "cards": []}
    logger.info(f"Found {len(today_items)} items")

    # Step 3: Cluster
    logger.info("Step 3: Clustering…")
    clustered = cluster_items(today_items)
    logger.info(f"Formed {len(clustered)} clusters: {list(clustered.keys())}")

    all_cards: list[dict] = []

    # Step 4: 1 related card — pick the best single cluster
    logger.info("Step 4: Selecting best related group…")
    related_groups = get_related_groups(clustered, n_groups=1, items_per_group=3)
    if related_groups:
        group = related_groups[0]
        logger.info(f"Analyzing related group ({len(group)} items from same cluster)…")
        try:
            cards = analyze_items(group, card_type="related")
            if cards:
                best = cards[0]  # already sorted by score desc
                all_cards.append(best)
                logger.info(f"  → Related card: {best.get('title', '?')[:50]}")
            else:
                logger.info("  → No related cards generated")
        except Exception as e:
            logger.error(f"  → Related analysis failed: {e}")
    else:
        logger.info("  → No eligible related groups")

    # Step 5: 1 cross-domain card — most distant cluster pair
    logger.info("Step 5: Selecting best cross-domain group…")
    cross_groups = get_crossdomain_groups(clustered, n_groups=1, items_per_group=2)
    if cross_groups:
        group = cross_groups[0]
        logger.info(f"Analyzing cross-domain group ({len(group)} items from different clusters)…")
        try:
            cards = analyze_items_crossdomain(group, card_type="crossdomain")
            if cards:
                best = cards[0]
                all_cards.append(best)
                logger.info(f"  → Cross-domain card: {best.get('title', '?')[:50]}")
            else:
                logger.info("  → No cross-domain cards generated")
        except Exception as e:
            logger.error(f"  → Cross-domain analysis failed: {e}")
    else:
        logger.info("  → No eligible cross-domain groups")

    # Step 6: Save
    if all_cards:
        save_cards(all_cards)
        logger.info(f"Step 6: Saved {len(all_cards)} cards")
    else:
        logger.info("Step 6: No cards to save")

    # Step 7: Mark analyzed
    analyzed_ids = [item["id"] for item in today_items]
    mark_analyzed(analyzed_ids)
    logger.info(f"Step 7: Marked {len(analyzed_ids)} items as analyzed")

    summary = f"Done — {len(all_cards)} cards: " + ", ".join(
        f"{c.get('card_type','?')}: {c.get('title','?')[:40]}" for c in all_cards
    )
    logger.info(summary)
    return {"message": f"Generated {len(all_cards)} cards", "cards": all_cards}


def _daily_job():
    """Wrapper for scheduler — logs errors instead of throwing."""
    try:
        run_generation_once()
    except Exception as e:
        logger.error(f"Scheduled generation failed: {e}")


def start_scheduler():
    """Start the background scheduler with a daily 08:30 trigger (Asia/Shanghai)."""
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(
        _daily_job,
        trigger=CronTrigger(hour=8, minute=30, timezone="Asia/Shanghai"),
        id="daily_opportunity_gen",
        name="Daily opportunity card generation",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started — daily job at 08:30 CST")


def stop_scheduler():
    """Shut down the scheduler gracefully."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=True)
        _scheduler = None
        logger.info("Scheduler stopped")
