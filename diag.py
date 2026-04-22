"""Inspecciona qué selectores funcionan en cada portal."""
import asyncio
import re
from playwright.async_api import async_playwright

TARGETS = [
    ("fotocasa", "https://www.fotocasa.es/es/alquiler/viviendas/sant-cugat-del-valles/todas-las-zonas/l?maxPrice=1500&minRooms=2"),
    ("habitaclia", "https://www.habitaclia.com/alquiler-sant_cugat_del_valles.htm?price_max=1500&room_min=2"),
    ("pisos", "https://www.pisos.com/alquiler/pisos-sant_cugat_del_valles/hasta-1500/2-habitaciones-mas/"),
]

CANDIDATE_SELECTORS = [
    "article",
    "article[class*='item']",
    "article[class*='card']",
    "article[class*='ad']",
    "article[class*='Card']",
    "div[class*='card']",
    "div[class*='Card']",
    "div[class*='item']",
    "div[class*='listing']",
    "div[class*='Listing']",
    "div[class*='Property']",
    "div[class*='product']",
    "li[class*='item']",
    "li[class*='card']",
    "[data-testid*='card']",
    "[data-testid*='item']",
    "[data-testid*='listing']",
    "[data-cy*='listing']",
]


async def inspect(name, url):
    print(f"\n{'='*70}")
    print(f"PORTAL: {name}")
    print(f"URL: {url}")
    print("=" * 70)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
            locale="es-ES",
            viewport={"width": 1366, "height": 820},
        )
        page = await ctx.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"  goto FAILED: {e}")
            await browser.close()
            return

        # Accept cookies
        for sel in ["#didomi-notice-agree-button", "button#onetrust-accept-btn-handler",
                    "button:has-text('Aceptar')", "button:has-text('Acepto')"]:
            try:
