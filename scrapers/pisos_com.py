"""Pisos.com scraper - updated selectors based on real HTML inspection."""
from __future__ import annotations

import re
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.models import Listing
from scrapers.base import BaseScraper


class PisosComScraper(BaseScraper):
    portal_name = "pisos"
    BASE = "https://www.pisos.com"

    async def scrape(self, config: dict) -> List[Listing]:
        from playwright.async_api import async_playwright, TimeoutError as PWTimeout

        out: List[Listing] = []
        max_pages = int(config.get("max_pages", 3))

        async with async_playwright() as pw:
            browser = await self._new_browser(pw)
            ctx = await self._new_context(browser)
            page = await ctx.new_page()

            for search in config.get("search_urls", []):
                base_url = search if isinstance(search, str) else search.get("url")
                location_label = "" if isinstance(search, str) else search.get("location", "")
                if not base_url:
                    continue

                for page_num in range(1, max_pages + 1):
                    url = base_url if page_num == 1 else self._paginate(base_url, page_num)
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    except PWTimeout:
                        break

                    await self._try_accept_cookies(page)
                    await self._polite_wait(1.5, 3.0)
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                    await self._polite_wait(1.0, 1.5)

                    html = await page.content()
                    items = self._parse(html, location_label)
                    print(f"[pisos] {url} -> {len(items)} items")
                    if not items:
                        break
                    out.extend(items)
                    await self._polite_wait(1.5, 3.0)

            await browser.close()
        return out

    def _paginate(self, url: str, n: int) -> str:
        clean = url.rstrip("/")
        return f"{clean}/{n}/"

    def _parse(self, html: str, location_label: str) -> List[Listing]:
        soup = BeautifulSoup(html, "lxml")
        out: List[Listing] = []

        # Per diagnostic: 54 div.ad-preview__product matches
        cards = (
            soup.select("div.ad-preview")
            or soup.select("div[class*='ad-preview']")
            or soup.select("div.ad-preview__product")
        )

        # Pisos sometimes wraps each card in a container; drill up if needed
        # But typically the 'ad-preview__product' is inside 'div.ad-preview'
        # We prefer the outer container if it has more info.
        seen_ids = set()
        for card in cards:
            # Find the link to the detail page (pattern: /alquiler/piso-...-NNNNNNNNN/)
            link_el = None
            for a in card.select("a[href]"):
                href = a.get("href", "")
                # Detail URLs end in /NNNNN/ and are under /alquiler/
                if re.search(r"/alquiler/[^/]+-\d{6,}/?$", href):
                    link_el = a
                    break
            if not link_el:
                # Fallback: any anchor ending in long number
                for a in card.select("a[href]"):
                    href = a.get("href", "")
                    if re.search(r"-\d{7,}/?$", href) and "/alquiler/" in href:
                        link_el = a
                        break

            if not link_el:
                continue

            href = link_el.get("href", "")
            url = urljoin(self.BASE, href)
            m = re.search(r"(\d{6,})/?$", url.rstrip("/"))
            if not m:
                continue
            ext_id = m.group(1)
            if ext_id in seen_ids:
                continue
            seen_ids.add(ext_id)

            title = link_el.get("title") or link_el.get_text(" ", strip=True) or "Anuncio Pisos.com"

            card_text = card.get_text(" ", strip=True)
            price = self._extract_price(card_text)
            if not price:
                continue

            rooms = self._extract_rooms(card_text)
            size = self._extract_size(card_text)

            out.append(Listing(
                portal=self.portal_name,
                external_id=ext_id,
                url=url,
                title=title[:200],
                price=price,
                rooms=rooms,
                size_m2=size,
                location=location_label,
            ))
        return out

    @staticmethod
    def _extract_price(text: str) -> int | None:
        if not text:
            return None
        matches = re.findall(r"(\d{3,5}(?:[\.,]\d{3})?)\s*€", text.replace("\u00a0", " "))
        for m in matches:
            n = int(re.sub(r"[^\d]", "", m))
            if 200 <= n <= 9000:
                return n
        return None

    @staticmethod
    def _extract_rooms(text: str) -> int | None:
        m = re.search(r"(\d+)\s*hab", text, re.I)
        return int(m.group(1)) if m else None

    @staticmethod
    def _extract_size(text: str) -> int | None:
        m = re.search(r"(\d{2,4})\s*m(?:²|2)?\b", text)
        if m:
            n = int(m.group(1))
            if 15 <= n <= 1000:
                return n
        return None
