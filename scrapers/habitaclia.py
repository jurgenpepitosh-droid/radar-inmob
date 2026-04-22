"""Habitaclia scraper - uses data-id and data-href attributes (stable)."""
from __future__ import annotations

import re
from typing import List

from bs4 import BeautifulSoup

from core.models import Listing
from scrapers.base import BaseScraper


class HabitacliaScraper(BaseScraper):
    portal_name = "habitaclia"
    BASE = "https://www.habitaclia.com"

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
                    print(f"[habitaclia] {url} -> {len(items)} items")
                    if not items:
                        break
                    out.extend(items)
                    await self._polite_wait(1.5, 3.0)

            await browser.close()
        return out

    def _paginate(self, url: str, n: int) -> str:
        if url.endswith(".htm"):
            return url.replace(".htm", f"-{n}.htm")
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}pag={n}"

    def _parse(self, html: str, location_label: str) -> List[Listing]:
        soup = BeautifulSoup(html, "lxml")
        out: List[Listing] = []

        cards = soup.select("article[data-id][data-href]")

        seen_ids = set()
        for card in cards:
            ext_id = card.get("data-id", "").strip()
            href = card.get("data-href", "").strip()
            if not ext_id or not href or ext_id in seen_ids:
                continue
            seen_ids.add(ext_id)

            url = href.split("?")[0]

            title = ""
            img = card.select_one("img[alt]")
            if img:
                title = img.get("alt", "").strip()
            if not title:
                h = card.select_one("h2, h3")
                if h:
                    title = h.get_text(" ", strip=True)
            if not title:
                title = "Anuncio Habitaclia"

            price = None
            price_el = card.select_one("span[itemprop='price']")
            if price_el:
                price = self._extract_price(price_el.get_text())
            if not price:
                price = self._extract_price(card.get_text(" ", strip=True))
            if not price:
                continue

            text = card.get_text(" ", strip=True)
            rooms = self._extract_rooms(text)
            size = self._extract_size(text)

            raw_loc = ""
            loc_el = card.select_one("[class*='location']") or card.select_one("span[class*='poblacion']")
            if loc_el:
                raw_loc = loc_el.get_text(" ", strip=True)[:200]

            out.append(Listing(
                portal=self.portal_name,
                external_id=ext_id,
                url=url,
                title=title[:200],
                price=price,
                rooms=rooms,
                size_m2=size,
                location=location_label,
                raw_location=raw_loc,
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
