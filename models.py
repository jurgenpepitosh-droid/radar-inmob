"""Telegram notifier."""
import os
from typing import List, Iterable
import httpx

from core.models import ListingChange

EMOJI = {
    "new": "🆕",
    "price_drop": "📉",
    "price_rise": "📈",
    "removed": "❌",
    "relisted": "♻️",
}

LABEL = {
    "new": "Nuevo anuncio",
    "price_drop": "BAJADA DE PRECIO",
    "price_rise": "Subida de precio",
    "removed": "Anuncio retirado",
    "relisted": "Re-publicado",
}


def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


class TelegramNotifier:
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "").strip()
        self.api = f"https://api.telegram.org/bot{self.token}" if self.token else None

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    async def send(self, text: str):
        if not self.enabled:
            print("[notifier] Telegram disabled (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)")
            return
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                r = await client.post(
                    f"{self.api}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": text,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": False,
                    },
                )
                if r.status_code >= 400:
                    print(f"[notifier] Telegram error {r.status_code}: {r.text[:300]}")
            except Exception as e:
                print(f"[notifier] Telegram failed: {e}")

    async def notify_changes(self, changes: List[ListingChange]):
        if not changes:
            return
        # Priority ordering so important stuff shows first
        priority = {"price_drop": 1, "new": 2, "relisted": 3, "price_rise": 4, "removed": 5}
        changes = sorted(changes, key=lambda c: (priority.get(c.change_type, 99), -(c.new_price or 0)))

        # Skip spamming on first-ever run if there are >50 "new" items — send a summary instead
        new_count = sum(1 for c in changes if c.change_type == "new")
        if new_count > 50:
            await self.send(
                f"🚀 <b>Primer escaneo</b>\nSe han indexado <b>{new_count}</b> anuncios activos. "
                "A partir de ahora solo te notificaré los <b>cambios</b> reales."
            )
            changes = [c for c in changes if c.change_type != "new"]

        for chunk in _chunks(changes, 8):
            await self.send(self._format_chunk(chunk))

    def _format_line(self, ch: ListingChange) -> str:
        l = ch.listing
        e = EMOJI.get(ch.change_type, "•")
        meta = " · ".join(filter(None, [
            f"{l.rooms}hab" if l.rooms else None,
            f"{l.size_m2}m²" if l.size_m2 else None,
            l.location or None,
            l.portal,
        ]))

        if ch.change_type == "price_drop":
            delta = abs(ch.price_delta or 0)
            pct = ch.price_delta_pct or 0
            return (
                f"{e} <b>{LABEL[ch.change_type]}</b> · -{delta}€ ({pct}%)\n"
                f"<b>{ch.old_price}€ → {ch.new_price}€</b>\n"
                f"<a href=\"{l.url}\">{l.title}</a>\n"
                f"<i>{meta}</i>"
            )
        if ch.change_type == "price_rise":
            delta = ch.price_delta or 0
            pct = ch.price_delta_pct or 0
            return (
                f"{e} <b>{LABEL[ch.change_type]}</b> · +{delta}€ ({pct}%)\n"
                f"<b>{ch.old_price}€ → {ch.new_price}€</b>\n"
                f"<a href=\"{l.url}\">{l.title}</a>\n"
                f"<i>{meta}</i>"
            )
        if ch.change_type in ("new", "relisted"):
            return (
                f"{e} <b>{LABEL[ch.change_type]}</b> · <b>{l.price}€</b>\n"
                f"<a href=\"{l.url}\">{l.title}</a>\n"
                f"<i>{meta}</i>"
            )
        # removed
        return (
            f"{e} <b>{LABEL[ch.change_type]}</b> (estaba a {ch.old_price}€)\n"
            f"<a href=\"{l.url}\">{l.title}</a>\n"
            f"<i>{meta}</i>"
        )

    def _format_chunk(self, changes: Iterable[ListingChange]) -> str:
        lines = ["<b>📡 Radar Inmobiliario</b>"]
        for ch in changes:
            lines.append(self._format_line(ch))
        return "\n\n".join(lines)
