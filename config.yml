"""Idealista scraper.

Strategy:
1. If RSS feeds are configured for a search → use feedparser (cheap, reliable).
2. Otherwise → Playwright against the search URL, parsing JSON-LD + DOM.

Idealista is AGGRESSIVELY anti-bot from datacenter IPs (GitHub Actions, AWS, GCP).
Configure a residential proxy via SCRAPER_PROXY env var for best reliability.
"""
from __future__ import annotations

import re
import json
from typing import List
from urllib.parse import urljoin

import httpx
import feedparser
from bs4 import BeautifulSoup

from core.models import Listing
from scrapers.base import BaseScraper


PRICE_RE = re.compile(r"([\d\.]+)")
ROOMS_RE = re.compile(r"(\d+)\s*hab", re.I)
SIZE_RE = re.compile(r"(\d+)\s*m")
ID_URL_RE = re.compile(r"/inmueble/(\d+)")


def _to_int(s: str) -> int | None:
    if not s:
        return None
    digits = re.sub(r"[^\d]", "", s)
    return int(digits) if digits else None


class IdealistaScraper(BaseScraper):
    portal_name = "idealista"
    BASE = "https://www.idealista.com"

    async def scrape(self, config: dict) -> List[Listing]:
        all_listings: List[Listing] = []

        # ---------- RSS path ----------
        for feed in config.get("rss_feeds", []) or []:
            url = feed if isinstance(feed, str) else feed.get("url")
            label = "" if isinstance(feed, str) else feed.get("label", "")
            if not url:
                continue
            try:
                rss_listings = await self._scrape_rss(url, location_label=label or config.get("default_location", ""))
                print(f"[idealista] RSS '{label or url}' → {len(rss_listings)} items")
                all_listings.extend(rss_listings)
            except Exception as e:
                print(f"[idealista] RSS error for {url}: {e}")

        # ---------- Playwright path ----------
        if config.get("search_urls"):
            try:
                pw_listings = await self._scrape_playwright(config)
                print(f"[idealista] Playwright → {len(pw_listings)} items")
                all_listings.extend(pw_listings)
            except Exception as e:
                print(f"[idealista] Playwright error: {e}")

        # Dedupe by uid
        seen = {}
        for l in all_listings:
            seen[l.uid] = l
        return list(seen.values())

    # ------------------------------------------------------------- RSS mode
    async def _scrape_rss(self, url: str, location_label: str = "") -> List[Listing]:
        async with httpx.AsyncClient(timeout=20, headers={"User-Agent": "Mozilla/5.0 RadarInmo/1.0"}) as client:
            r = await client.get(url)
            r.raise_for_status()
            content = r.text

        parsed = feedparser.parse(content)
        out: List[Listing] = []
        for entry in parsed.entries:
            link = entry.get("link", "")
            m = ID_URL_RE.search(link)
            if not m:
                continue
            ext_id = m.group(1)
            title = entry.get("title", "").strip()
            description = entry.get("summary", "").strip()
            # Price is typically in title like "Piso en alquiler - 1.200 €/mes"
            price = self._parse_price_from_text(title) or self._parse_price_from_text(description)
            if not price:
                continue
            rooms = self._parse_rooms_from_text(f"{title} {description}")
            size = self._parse_size_from_text(f"{title} {description}")

            out.append(Listing(
                portal=self.portal_name,
                external_id=ext_id,
                url=link,
                title=BeautifulSoup(title, "lxml").get_text(" ", strip=True),
                price=price,
                rooms=rooms,
                size_m2=size,
                location=location_label,
                raw_location="",
                description=BeautifulSoup(description, "lxml").get_text(" ", strip=True)[:500],
            ))
        return out

    # ------------------------------------------------------ Playwright mode
    async def _scrape_playwright(self, config: dict) -> List[Listing]:
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
                        print(f"[idealista] timeout {url}")
                        break

                    await self._try_accept_cookies(page)
                    await self._polite_wait(1.5, 3.0)

                    # Detect block page
                    title = (await page.title()) or ""
                    if "blocked" in title.lower() or "captcha" in (await page.content()).lower()[:3000]:
                        print(f"[idealista] BLOCKED on {url} — consider proxy (SCRAPER_PROXY)")
                        break

                    html = await page.content()
                    items = self._parse_search_html(html, location_label)
                    if not items:
                        break
                    out.extend(items)
                    await self._polite_wait(2.0, 4.0)

            await browser.close()
        return out

    def _paginate(self, url: str, n: int) -> str:
        # Idealista pagination: append "pagina-N.htm" before query
        if url.endswith("/"):
            return f"{url}pagina-{n}.htm"
        if ".htm" in url:
            return url.replace(".htm", f"/pagina-{n}.htm")
        return f"{url}/pagina-{n}.htm"

    def _parse_search_html(self, html: str, location_label: str) -> List[Listing]:
        soup = BeautifulSoup(html, "lxml")
        out: List[Listing] = []

        # Item containers on Idealista search pages
        items = soup.select("article.item") or soup.select("article[data-element-id]")
        for art in items:
            link_el = art.select_one("a.item-link") or art.select_one("a[href*='/inmueble/']")
            if not link_el:
                continue
            href = link_el.get("href", "")
            url = urljoin(self.BASE, href)
            m = ID_URL_RE.search(url)
            if not m:
                continue
            ext_id = m.group(1)

            title = link_el.get("title") or link_el.get_text(" ", strip=True)

            price_el = art.select_one(".item-price") or art.select_one("[class*='price']")
            price = self._parse_price_from_text(price_el.get_text() if price_el else "")
            if not price:
                continue

            detail_text = art.select_one(".item-detail-char")
            detail_str = detail_text.get_text(" ", strip=True) if detail_text else ""
            rooms = self._parse_rooms_from_text(detail_str)
            size = self._parse_size_from_text(detail_str)

            loc_el = art.select_one(".item-detail-parent") or art.select_one("[class*='location']")
            raw_loc = loc_el.get_text(" ", strip=True) if loc_el else ""

            description_el = art.select_one(".item-description") or art.select_one("p[class*='description']")
            description = description_el.get_text(" ", strip=True)[:500] if description_el else ""

            images = []
            for img in art.select("img")[:4]:
                src = img.get("src") or img.get("data-src") or ""
                if src.startswith("http"):
                    images.append(src)

            out.append(Listing(
                portal=self.portal_name,
                external_id=ext_id,
                url=url,
                title=title,
                price=price,
                rooms=rooms,
                size_m2=size,
                location=location_label,
                raw_location=raw_loc,
                description=description,
                images=images,
            ))
        return out

    # -------------------------------------------------------- parse helpers
    @staticmethod
    def _parse_price_from_text(text: str) -> int | None:
        if not text:
            return None
        m = re.search(r"([\d\.]+)\s*€", text)
        if not m:
            m = re.search(r"([\d\.]+)", text)
        return _to_int(m.group(1)) if m else None

    @staticmethod
    def _parse_rooms_from_text(text: str) -> int | None:
        m = ROOMS_RE.search(text or "")
        return int(m.group(1)) if m else None

    @staticmethod
    def _parse_size_from_text(text: str) -> int | None:
        m = SIZE_RE.search(text or "")
        return int(m.group(1)) if m else None
