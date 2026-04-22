"""Pisos.com scraper - uses id and data-lnk-href attributes (stable)."""
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

        # Pisos cards have data-lnk-href on the outer div.ad-preview
        cards = soup.select("div.ad-preview[data-lnk-href]")

        seen_ids = set()
        for card in cards:
            href = card.get("data-lnk-href", "").strip()
            if not href:
                continue
            url = urljoin(self.BASE, href)

            # Extract external_id from the div's id attribute (format: "63386499540.106400")
            # or as fallback from the URL
            ext_id = card.get("id", "").strip()
            if not ext_id:
                m = re.search(r"-(\d+[_\d]*)/?$", href)
                if m:
                    ext_id = m.group(1)
            if not ext_id or ext_id in seen_ids:
                continue
            seen_ids.add(ext_id)

            # Title: img alt inside the carousel
            title = ""
            img = card.select_one("img[alt]")
            if img:
                title = img.get("alt", "").strip()
            if not title:
                title = "Anuncio Pisos.com"

            # Price: explicit selector span.ad-preview__price
            price = None
            price_el = card.select_one("span.ad-preview__price")
            if price_el:
                # Price text is "1.050 €/mes" - strip "/mes" by taking only the main number
                price_text = price_el.get_text(" ", strip=True)
                price = self._extract_price(price_text)
            if not price:
                price = self._extract_price(card.get_text(" ", strip=True))
            if not price:
                continue

            text = card.get_text(" ", strip=True)
            rooms = self._extract_rooms(text)
            size = self._extract_size(text)

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
        # "1.050 €" or "1050€" - take first plausible rent number
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
