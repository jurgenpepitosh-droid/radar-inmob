"""Inspecciona que selectores funcionan en cada portal."""
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
        cookie_selectors = [
            "#didomi-notice-agree-button",
            "button#onetrust-accept-btn-handler",
            "button:has-text('Aceptar')",
            "button:has-text('Acepto')",
        ]
        for sel in cookie_selectors:
            try:
                b = page.locator(sel).first
                if await b.count() and await b.is_visible(timeout=800):
                    await b.click(timeout=1500)
                    print(f"  cookies accepted via {sel}")
                    break
            except Exception:
                continue

        await asyncio.sleep(3)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
        await asyncio.sleep(2)

        title = await page.title()
        html = await page.content()
        print(f"  page title: {title}")
        print(f"  html length: {len(html)}")

        # Detect block
        if "blocked" in title.lower() or "captcha" in html.lower()[:4000]:
            print("  !!! BLOCKED or CAPTCHA page !!!")

        # Count listings-looking elements by selector
        print("\n  Candidate selectors (count):")
        results = []
        for sel in CANDIDATE_SELECTORS:
            try:
                count = await page.locator(sel).count()
                if count > 0:
                    results.append((count, sel))
            except Exception:
                continue
        for count, sel in sorted(results, reverse=True)[:15]:
            print(f"    {count:>4}  {sel}")

        # Sample href patterns in page
        hrefs = re.findall(r'href="([^"]+)"', html)
        relevant = [h for h in hrefs if any(k in h.lower() for k in ["alquiler", "inmueble", "piso", "/d-"])][:10]
        print("\n  Sample 'listing-like' href patterns:")
        for h in relevant[:8]:
            print(f"    {h[:100]}")

        # Sample class names of top-candidate children
        if results:
            top_count, top_sel = sorted(results, reverse=True)[0]
            print(f"\n  Classes of first 3 matches of '{top_sel}':")
            for i in range(min(3, top_count)):
                try:
                    cls = await page.locator(top_sel).nth(i).get_attribute("class")
                    if cls:
                        print(f"    [{i}] {cls[:150]}")
                    else:
                        print(f"    [{i}] (none)")
                except Exception:
                    continue

        await browser.close()


async def main():
    for name, url in TARGETS:
        try:
            await inspect(name, url)
        except Exception as e:
            print(f"  {name} inspect failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
