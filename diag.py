"""Extrae HTML real de una card de cada portal para ver su estructura."""
import asyncio
from playwright.async_api import async_playwright


TARGETS = [
    ("habitaclia", "https://www.habitaclia.com/alquiler-sant_cugat_del_valles.htm?price_max=1500&room_min=2"),
    ("pisos", "https://www.pisos.com/alquiler/pisos-sant_cugat_del_valles/hasta-1500/2-habitaciones-mas/"),
]


async def inspect_card(name, url):
    print(f"\n{'#' * 70}")
    print(f"# PORTAL: {name}")
    print(f"# URL: {url}")
    print(f"{'#' * 70}")

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

        for sel in ["#didomi-notice-agree-button", "button#onetrust-accept-btn-handler",
                    "button:has-text('Aceptar')", "button:has-text('Acepto')"]:
            try:
                b = page.locator(sel).first
                if await b.count() and await b.is_visible(timeout=800):
                    await b.click(timeout=1500)
                    break
            except Exception:
                continue

        await asyncio.sleep(3)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
        await asyncio.sleep(2)

        candidates = [
            "article.list-item",
            "article[class*='list-item']",
            "div.ad-preview",
            "div[class*='ad-preview']:not([class*='product']):not([class*='badge'])",
            "article[class*='item']",
            "article",
            "li.list-item",
        ]

        for candidate in candidates:
            try:
                count = await page.locator(candidate).count()
                if count > 0:
                    print(f"\n--- Trying '{candidate}' (count={count}) ---")
                    for i in range(min(2, count)):
                        html = await page.locator(candidate).nth(i).evaluate("e => e.outerHTML")
                        snippet = html[:3500]
                        print(f"\n### MATCH [{i}] length={len(html)}")
                        print(snippet)
                        print(f"### END MATCH [{i}]")
                    break
            except Exception as e:
                print(f"  '{candidate}' failed: {e}")
                continue

        await browser.close()


async def main():
    for name, url in TARGETS:
        await inspect_card(name, url)


if __name__ == "__main__":
    asyncio.run(main())
