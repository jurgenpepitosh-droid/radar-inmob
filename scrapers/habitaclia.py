"""Habitaclia scraper - updated selectors based on real HTML inspection."""
from __future__ import annotations

import re
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.models import Listing
from scrapers.base import BaseScraper

ID_RE = re.compile(r"-(\d{5,})\.htm")


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

                    # Scroll to trigger lazy-loaded images
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

        # Per diagnostic: top selectors are 'article[class*='item']' (30)
        # and the cards use class 'list-item' (30 matches)
        cards = soup.select("article.list-item") or soup.select("article[class*='list-item']")
        if not cards:
            cards = soup.select("article[class*='item']")

        seen_ids = set()
        for card in cards:
            # The card has multiple links; we need one pointing to a detail page
            # Detail links match pattern /alquiler-...-NNNNN.htm or similar
            link_el = None
            for a in card.select("a[href]"):
                href = a.get("href", "")
                if ID_RE.search(href):
                    link_el = a
                    break
            if not link_el:
                continue

            href = link_el.get("href", "")
            url = urljoin(self.BASE, href)
            m = ID_RE.search(url)
            if not m:
                continue
            ext_id = m.group(1)
            if ext_id in seen_ids:
                continue
            seen_ids.add(ext_id)

            title = (
                link_el.get("title")
                or link_el.get_text(" ", strip=True)
                or "Anuncio Habitaclia"
            )

            # Price: look for € sign anywhere in the card
            card_text = card.get_text(" ", strip=True)
            price = self._extract_price(card_text)
            if not price:
                continue

            rooms = self._extract_rooms(card_text)
            size = self._extract_size(card_text)

            # Location within the card
            loc_el = (
                card.select_one("[class*='location']")
                or card.select_one("[class*='poblacion']")
                or card.select_one("h3 a, h2 a")
            )
            raw_loc = loc_el.get_text(" ", strip=True) if loc_el else ""

            out.append(Listing(
                portal=self.portal_name,
                external_id=ext_id,
                url=url,
                title=title[:200],
                price=price,
                rooms=rooms,
                size_m2=size,
                location=location_label,
                raw_location=raw_loc[:200],
            ))
        return out

    @staticmethod
    def _extract_price(text: str) -> int | None:
        if not text:
            return None
        # Find patterns like "1.200 €" or "1200€" - rent only (avoid prices >10000)
        matches = re.findall(r"(\d{3,5}(?:[\.,]\d{3})?)\s*€", text.replace("\u00a0", " "))
        for m in matches:
            n = int(re.sub(r"[^\d]", "", m))
            if 200 <= n <= 9000:  # plausible rent range
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
