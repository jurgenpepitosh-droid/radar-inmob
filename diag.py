"""Audita todos los archivos comparando tamaños y primera línea."""
import os

EXPECTED = {
    "main.py":              (3200, '"""Entry point for the scraper.'),
    "config.yml":           (2000, "db_path: data/listings.db"),
    "requirements.txt":     (150, "playwright==1.47.0"),
    "core/__init__.py":     (0, ""),
    "core/models.py":       (1500, '"""Core data models."""'),
    "core/storage.py":      (10000, '"""SQLite storage'),
    "core/notifier.py":     (4500, '"""Telegram notifier."""'),
    "scrapers/__init__.py": (570, '"""Scraper registry'),
    "scrapers/base.py":     (3400, '"""Base scraper'),
    "scrapers/idealista.py":(9000, '"""Idealista scraper.'),
    "scrapers/fotocasa.py": (5000, '"""Fotocasa scraper'),
    "scrapers/habitaclia.py":(4200, '"""Habitaclia scraper'),
    "scrapers/pisos_com.py":(4000, '"""Pisos.com scraper."""'),
}

print("=" * 70)
print("AUDITORÍA")
print("=" * 70)
print(f"{'FILE':<30} {'SIZE':>8} {'EXPECTED':>10} {'STATUS':<10}")
print("-" * 70)

problems = []
for path, (expected_size, expected_start) in EXPECTED.items():
    if not os.path.exists(path):
        print(f"{path:<30} {'-':>8} {expected_size:>10} MISSING")
        problems.append(path)
        continue
    content = open(path, encoding="utf-8", errors="replace").read()
    size = len(content)
    first_line = content.split("\n", 1)[0][:50] if content else "(empty)"

    ok_size = size > expected_size * 0.7  # at least 70% of expected
    ok_start = (expected_start == "" and size < 20) or first_line.startswith(expected_start[:25])
    status = "OK" if (ok_size and ok_start) else "BROKEN"
    if status == "BROKEN":
        problems.append(path)

    print(f"{path:<30} {size:>8} {expected_size:>10} {status:<10}")
    if status == "BROKEN":
        print(f"  └─ first line: {first_line!r}")

print("=" * 70)
print(f"BROKEN FILES ({len(problems)}):")
for p in problems:
    print(f"  - {p}")
print("=" * 70)
