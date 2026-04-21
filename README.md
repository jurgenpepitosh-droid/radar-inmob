"""Base scraper contract + shared Playwright helpers."""
from __future__ import annotations

import asyncio
import random
import os
from abc import ABC, abstractmethod
from typing import List, Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from core.models import Listing


USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
]


class BaseScraper(ABC):
    portal_name: str = ""

    def __init__(self, proxy: Optional[str] = None):
        # Optional proxy — set SCRAPER_PROXY env var to enable
        self.proxy = proxy or os.getenv("SCRAPER_PROXY")

    @abstractmethod
    async def scrape(self, config: dict) -> List[Listing]:
        """Return all listings found for the given search config."""
        ...

    # ------------------------------------------------- Playwright helpers
    async def _new_browser(self, playwright) -> Browser:
        launch_args = {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        }
        if self.proxy:
            launch_args["proxy"] = {"server": self.proxy}
        return await playwright.chromium.launch(**launch_args)

    async def _new_context(self, browser: Browser) -> BrowserContext:
        ctx = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1366, "height": 820},
            locale="es-ES",
            timezone_id="Europe/Madrid",
            extra_http_headers={
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.6",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        # Light fingerprint scrubbing — we don't pull in heavy stealth libs on CI
        await ctx.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['es-ES','es','en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            window.chrome = { runtime: {} };
            """
        )
        return ctx

    async def _polite_wait(self, min_s: float = 1.5, max_s: float = 3.0):
        await asyncio.sleep(random.uniform(min_s, max_s))

    async def _try_accept_cookies(self, page: Page):
        """Best-effort cookie banner dismissal — selectors vary per portal."""
        selectors = [
            "#didomi-notice-agree-button",
            "button#onetrust-accept-btn-handler",
            "button[data-testid='TcfAccept']",
            "button:has-text('Aceptar')",
            "button:has-text('Aceptar todo')",
            "button:has-text('Acepto')",
        ]
        for sel in selectors:
            try:
                btn = page.locator(sel).first
                if await btn.count() and await btn.is_visible(timeout=800):
                    await btn.click(timeout=1500)
                    await self._polite_wait(0.5, 1.0)
                    return
            except Exception:
                continue
