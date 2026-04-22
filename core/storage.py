"""SQLite storage with change detection and JSON export for the dashboard."""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timezone

from core.models import Listing, ListingChange


class Storage:
    def __init__(self, db_path: str = "data/listings.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    # ------------------------------------------------------------------ schema
    def _init_schema(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS listings (
                uid TEXT PRIMARY KEY,
                portal TEXT NOT NULL,
                external_id TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                price INTEGER NOT NULL,
                rooms INTEGER,
                bathrooms INTEGER,
                size_m2 INTEGER,
                location TEXT,
                raw_location TEXT,
                description TEXT,
                images_json TEXT,
                features_json TEXT,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT NOT NULL,
                price INTEGER NOT NULL,
                recorded_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT NOT NULL,
                event_type TEXT NOT NULL,
                old_price INTEGER,
                new_price INTEGER,
                occurred_at TEXT NOT NULL,
                notified INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_listings_portal ON listings(portal);
            CREATE INDEX IF NOT EXISTS idx_listings_active ON listings(is_active);
            CREATE INDEX IF NOT EXISTS idx_events_notified ON events(notified);
            CREATE INDEX IF NOT EXISTS idx_price_history_uid ON price_history(uid);
            """
        )
        self.conn.commit()

    # ----------------------------------------------------------- core methods
    def _row_to_listing(self, row: sqlite3.Row) -> Listing:
        return Listing(
            portal=row["portal"],
            external_id=row["external_id"],
            url=row["url"],
            title=row["title"],
            price=row["price"],
            rooms=row["rooms"],
            bathrooms=row["bathrooms"],
            size_m2=row["size_m2"],
            location=row["location"] or "",
            raw_location=row["raw_location"] or "",
            description=row["description"] or "",
            images=json.loads(row["images_json"] or "[]"),
            features=json.loads(row["features_json"] or "[]"),
        )

    def get_active(self) -> Dict[str, Listing]:
        rows = self.conn.execute(
            "SELECT * FROM listings WHERE is_active=1"
        ).fetchall()
        return {r["uid"]: self._row_to_listing(r) for r in rows}

    def exists_inactive(self, uid: str) -> bool:
        return bool(
            self.conn.execute(
                "SELECT 1 FROM listings WHERE uid=? AND is_active=0", (uid,)
            ).fetchone()
        )

    def _insert_listing(self, l: Listing, now: str, is_new: bool = True):
        if self.exists_inactive(l.uid):
            self.conn.execute(
                """
                UPDATE listings SET
                    url=?, title=?, price=?, rooms=?, bathrooms=?, size_m2=?,
                    location=?, raw_location=?, description=?, images_json=?,
                    features_json=?, last_seen=?, is_active=1
                WHERE uid=?
                """,
                (
                    l.url, l.title, l.price, l.rooms, l.bathrooms, l.size_m2,
                    l.location, l.raw_location, l.description,
                    json.dumps(l.images), json.dumps(l.features),
                    now, l.uid,
                ),
            )
        else:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO listings (
                    uid, portal, external_id, url, title, price, rooms, bathrooms,
                    size_m2, location, raw_location, description, images_json,
                    features_json, first_seen, last_seen, is_active
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)
                """,
                (
                    l.uid, l.portal, l.external_id, l.url, l.title, l.price,
                    l.rooms, l.bathrooms, l.size_m2, l.location, l.raw_location,
                    l.description, json.dumps(l.images), json.dumps(l.features),
                    now, now,
                ),
            )
        self._record_price(l.uid, l.price, now)

    def _update_listing(self, l: Listing, now: str):
        self.conn.execute(
            """
            UPDATE listings SET
                url=?, title=?, price=?, rooms=?, bathrooms=?, size_m2=?,
                location=?, raw_location=?, description=?, images_json=?,
                features_json=?, last_seen=?, is_active=1
            WHERE uid=?
            """,
            (
                l.url, l.title, l.price, l.rooms, l.bathrooms, l.size_m2,
                l.location, l.raw_location, l.description,
                json.dumps(l.images), json.dumps(l.features),
                now, l.uid,
            ),
        )

    def _record_price(self, uid: str, price: int, now: str):
        last = self.conn.execute(
            "SELECT price FROM price_history WHERE uid=? ORDER BY id DESC LIMIT 1",
            (uid,),
        ).fetchone()
        if not last or last["price"] != price:
            self.conn.execute(
                "INSERT INTO price_history (uid, price, recorded_at) VALUES (?,?,?)",
                (uid, price, now),
            )

    # --------------------------------------------------------- diff detection
    def upsert_and_diff(self, listings: List[Listing]) -> List[ListingChange]:
        """Upsert all scraped listings and return detected changes.

        Removals are detected per-portal: a listing is marked inactive only
        when we scraped its portal in this run and it's no longer there.
        """
        now = datetime.now(timezone.utc).isoformat()
        existing = self.get_active()
        all_seen_uids = set()
        changes: List[ListingChange] = []
        portals_scraped = {l.portal for l in listings}

        for l in listings:
            all_seen_uids.add(l.uid)
            prior = existing.get(l.uid)

            if not prior:
                was_inactive = self.exists_inactive(l.uid)
                change_type = "relisted" if was_inactive else "new"
                changes.append(
                    ListingChange(listing=l, change_type=change_type, new_price=l.price)
                )
                self._insert_listing(l, now)
            else:
                if l.price != prior.price:
                    ct = "price_drop" if l.price < prior.price else "price_rise"
                    changes.append(
                        ListingChange(
                            listing=l, change_type=ct,
                            old_price=prior.price, new_price=l.price,
                        )
                    )
                self._update_listing(l, now)
                self._record_price(l.uid, l.price, now)

        # Removal detection — only for portals we actually scraped this run
        for uid, prior in existing.items():
            if prior.portal in portals_scraped and uid not in all_seen_uids:
                self.conn.execute(
                    "UPDATE listings SET is_active=0, last_seen=? WHERE uid=?",
                    (now, uid),
                )
                changes.append(
                    ListingChange(listing=prior, change_type="removed", old_price=prior.price)
                )

        # Log events
        for ch in changes:
            self.conn.execute(
                """
                INSERT INTO events (uid, event_type, old_price, new_price, occurred_at)
                VALUES (?,?,?,?,?)
                """,
                (ch.listing.uid, ch.change_type, ch.old_price, ch.new_price, now),
            )
        self.conn.commit()
        return changes

    # --------------------------------------------------------------- exports
    def export_json(self, path: str = "data/listings.json"):
        """Snapshot state for the public dashboard."""
        listings_rows = self.conn.execute(
            "SELECT * FROM listings ORDER BY is_active DESC, last_seen DESC"
        ).fetchall()

        listings_payload = []
        for r in listings_rows:
            d = dict(r)
            d["images"] = json.loads(d.pop("images_json") or "[]")
            d["features"] = json.loads(d.pop("features_json") or "[]")
            d["uid"] = r["uid"]
            d["is_active"] = bool(r["is_active"])
            listings_payload.append(d)

        events = [
            dict(r) for r in self.conn.execute(
                """
                SELECT e.*, l.title, l.url, l.portal, l.location, l.rooms, l.size_m2
                FROM events e JOIN listings l ON e.uid=l.uid
                ORDER BY e.occurred_at DESC LIMIT 500
                """
            ).fetchall()
        ]

        price_hist = {}
        for r in self.conn.execute(
            "SELECT uid, price, recorded_at FROM price_history ORDER BY id ASC"
        ).fetchall():
            price_hist.setdefault(r["uid"], []).append(
                {"price": r["price"], "at": r["recorded_at"]}
            )

        by_portal: Dict[str, int] = {}
        for l in listings_payload:
            if l["is_active"]:
                by_portal[l["portal"]] = by_portal.get(l["portal"], 0) + 1

        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "active_total": sum(1 for l in listings_payload if l["is_active"]),
                "inactive_total": sum(1 for l in listings_payload if not l["is_active"]),
                "by_portal": by_portal,
            },
            "listings": listings_payload,
            "events": events,
            "price_history": price_hist,
        }
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    # ------------------------------------------------------------------ misc
    def mark_notified(self, uids: List[str]):
        if not uids:
            return
        qmarks = ",".join("?" * len(uids))
        self.conn.execute(
            f"UPDATE events SET notified=1 WHERE notified=0 AND uid IN ({qmarks})",
            uids,
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
