"""Habitaclia scraper — part of Adevinta group, generally scraper-tolerant."""
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

                    html = await page.content()
                    items = self._parse(html, location_label)
                    if not items:
                        break
                    out.extend(items)
                    await self._polite_wait(1.5, 3.0)

            await browser.close()
        return out

    def _paginate(self, url: str, n: int) -> str:
        # Habitaclia: append -N.htm or ?pag=N
        if url.endswith(".htm"):
            return url.replace(".htm", f"-{n}.htm")
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}pag={n}"

    def _parse(self, html: str, location_label: str) -> List[Listing]:
        soup = BeautifulSoup(html, "lxml")
        out: List[Listing] = []

        cards = soup.select("article.list-item-container, article.list-item, article[class*='item']")
        for card in cards:
            link_el = card.select_one("a[href*='.htm']")
            if not link_el:
                continue
            href = link_el.get("href", "")
            url = urljoin(self.BASE, href)
            m = ID_RE.search(url)
            if not m:
                continue
            ext_id = m.group(1)

            title_el = card.select_one("h3, h2, .list-item-title")
            title = title_el.get_text(" ", strip=True) if title_el else "Anuncio Habitaclia"

            price_el = card.select_one(".list-item-price, [class*='price']")
            price = self._extract_price(price_el.get_text() if price_el else "")
            if not price:
                continue

            feats_text = " ".join(
                el.get_text(" ", strip=True) for el in card.select(".list-item-feature, .feature, li")
            )
            rooms = self._extract_rooms(feats_text)
            size = self._extract_size(feats_text)

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
        m = re.search(r"([\d\.]+)\s*€", text.replace("\u00a0", " "))
        if not m:
            return None
        return int(re.sub(r"[^\d]", "", m.group(1)))

    @staticmethod
    def _extract_rooms(text: str) -> int | None:
        m = re.search(r"(\d+)\s*hab", text, re.I)
        return int(m.group(1)) if m else None

    @staticmethod
    def _extract_size(text: str) -> int | None:
        m = re.search(r"(\d+)\s*m", text)
        return int(m.group(1)) if m else None
