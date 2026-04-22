"""Entry point for the scraper.

Usage:
    python main.py                # Run all enabled portals
    python main.py --dry-run      # Run without committing changes / notifying
    python main.py --portals idealista,fotocasa  # Only specific portals
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import traceback
from pathlib import Path

import yaml

from core.storage import Storage
from core.notifier import TelegramNotifier
from core.models import Listing
from scrapers import REGISTRY


DEFAULT_CONFIG_PATH = "config.yml"


def apply_filters(listings: list[Listing], defaults: dict) -> list[Listing]:
    """Apply global filters (max_price, min_rooms)."""
    max_price = defaults.get("max_price")
    min_rooms = defaults.get("min_rooms")
    out = []
    for l in listings:
        if max_price and l.price and l.price > max_price:
            continue
        if min_rooms and l.rooms and l.rooms < min_rooms:
            continue
        out.append(l)
    return out


async def run(config_path: str, only_portals: list[str] | None, dry_run: bool) -> int:
    cfg = yaml.safe_load(Path(config_path).read_text())
    defaults = cfg.get("defaults", {}) or {}
    portals_cfg = cfg.get("portals", {}) or {}

    storage = Storage(cfg.get("db_path", "data/listings.db"))
    notifier = TelegramNotifier()

    all_listings: list[Listing] = []
    errors: list[str] = []

    for portal_name, portal_cfg in portals_cfg.items():
        if not portal_cfg.get("enabled", True):
            continue
        if only_portals and portal_name not in only_portals:
            continue
        if portal_name not in REGISTRY:
            print(f"[main] unknown portal '{portal_name}' - skipping")
            continue

        ScraperCls = REGISTRY[portal_name]
        scraper = ScraperCls()
        print(f"\n=== {portal_name.upper()} ===")
        try:
            items = await scraper.scrape(portal_cfg)
            items = apply_filters(items, defaults)
            print(f"[main] {portal_name}: {len(items)} listings after filters")
            all_listings.extend(items)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"[main] {portal_name} FAILED:\n{tb}")
            errors.append(f"{portal_name}: {e}")

    print(f"\n[main] Total scraped: {len(all_listings)}")

    if dry_run:
        print("[main] DRY RUN - not writing to DB or sending notifications")
        return 0

    # Diff + persist
    changes = storage.upsert_and_diff(all_listings)
    print(f"[main] Changes detected: {len(changes)}")
    by_type = {}
    for ch in changes:
        by_type[ch.change_type] = by_type.get(ch.change_type, 0) + 1
    for k, v in by_type.items():
        print(f"  {k}: {v}")

    # Notify
    try:
        await notifier.notify_changes(changes)
        storage.mark_notified([ch.listing.uid for ch in changes])
    except Exception as e:
        print(f"[main] notify failed: {e}")

    # Export dashboard snapshot
    storage.export_json(cfg.get("json_path", "data/listings.json"))
    storage.close()

    if errors and len(errors) == len(portals_cfg):
        return 1
    return 0


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    p.add_argument("--portals", default="", help="Comma-separated subset")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    portals = [p.strip() for p in args.portals.split(",") if p.strip()] or None
    code = asyncio.run(run(args.config, portals, args.dry_run))
    sys.exit(code)
