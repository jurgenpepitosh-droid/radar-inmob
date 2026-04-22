"""Script de diagnóstico para saber qué está pasando."""
import sys
import os
import traceback

print("=" * 60, flush=True)
print("DIAG · Python version:", sys.version, flush=True)
print("DIAG · cwd:", os.getcwd(), flush=True)
print("DIAG · files:", sorted(os.listdir("."))[:30], flush=True)
print("=" * 60, flush=True)

print("\n>>> Test 1: import yaml", flush=True)
try:
    import yaml
    print("   OK", flush=True)
except Exception as e:
    print("   FAIL:", e, flush=True)
    traceback.print_exc()

print("\n>>> Test 2: load config.yml", flush=True)
try:
    cfg = yaml.safe_load(open("config.yml").read())
    print("   OK · portals:", list(cfg.get("portals", {}).keys()), flush=True)
except Exception as e:
    print("   FAIL:", e, flush=True)
    traceback.print_exc()

print("\n>>> Test 3: import core modules", flush=True)
try:
    sys.path.insert(0, ".")
    from core.models import Listing
    from core.storage import Storage
    from core.notifier import TelegramNotifier
    print("   OK", flush=True)
except Exception as e:
    print("   FAIL:", e, flush=True)
    traceback.print_exc()

print("\n>>> Test 4: import scrapers", flush=True)
try:
    from scrapers import REGISTRY
    print("   OK · registry keys:", list(REGISTRY.keys()), flush=True)
except Exception as e:
    print("   FAIL:", e, flush=True)
    traceback.print_exc()

print("\n>>> Test 5: basic HTTP fetch (github.com)", flush=True)
try:
    import httpx
    r = httpx.get("https://www.github.com", timeout=10, follow_redirects=True)
    print(f"   OK · status: {r.status_code}", flush=True)
except Exception as e:
    print("   FAIL:", e, flush=True)

print("\n>>> Test 6: fetch idealista homepage (no scraping)", flush=True)
try:
    r = httpx.get(
        "https://www.idealista.com/",
        timeout=15,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36"},
    )
    print(f"   status: {r.status_code} · length: {len(r.text)}", flush=True)
    if r.status_code == 403 or "blocked" in r.text.lower()[:2000]:
        print("   → Idealista BLOQUEA la IP del runner. Necesitamos proxy.", flush=True)
    elif r.status_code == 200:
        print("   → Idealista acepta la IP. El problema está en los selectores.", flush=True)
except Exception as e:
    print("   FAIL:", e, flush=True)

print("\n>>> Test 7: fetch fotocasa homepage", flush=True)
try:
    r = httpx.get(
        "https://www.fotocasa.es/",
        timeout=15,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36"},
    )
    print(f"   status: {r.status_code} · length: {len(r.text)}", flush=True)
except Exception as e:
    print("   FAIL:", e, flush=True)

print("\n>>> Test 8: playwright import", flush=True)
try:
    from playwright.async_api import async_playwright
    print("   OK", flush=True)
except Exception as e:
    print("   FAIL:", e, flush=True)
    traceback.print_exc()

print("\n" + "=" * 60, flush=True)
print("DIAG COMPLETE", flush=True)
print("=" * 60, flush=True)
