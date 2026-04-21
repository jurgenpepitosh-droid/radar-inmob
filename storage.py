name: Scrape & Notify

on:
  schedule:
    # Cada 30 minutos. Nota: GitHub Actions puede retrasarse varios minutos
    # bajo carga alta; esto es normal y aceptable.
    - cron: "*/30 * * * *"
  workflow_dispatch:
    inputs:
      dry_run:
        description: "Dry run (no notificar, no guardar)"
        required: false
        default: "false"

concurrency:
  group: scrape
  cancel-in-progress: false

permissions:
  contents: write  # to commit data back
  pages: write
  id-token: write

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 12
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Cache Playwright browsers
        uses: actions/cache@v4
        id: pw-cache
        with:
          path: ~/.cache/ms-playwright
          key: playwright-chromium-${{ hashFiles('requirements.txt') }}

      - name: Install Playwright Chromium
        if: steps.pw-cache.outputs.cache-hit != 'true'
        run: python -m playwright install chromium --with-deps

      - name: Install Playwright system deps (cached browser)
        if: steps.pw-cache.outputs.cache-hit == 'true'
        run: python -m playwright install-deps chromium

      - name: Run scraper
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          SCRAPER_PROXY: ${{ secrets.SCRAPER_PROXY }}
        run: |
          if [ "${{ github.event.inputs.dry_run }}" = "true" ]; then
            python main.py --dry-run
          else
            python main.py
          fi

      - name: Commit data updates
        if: github.event.inputs.dry_run != 'true'
        run: |
          git config user.name "scraper-bot"
          git config user.email "scraper-bot@users.noreply.github.com"
          git add data/listings.db data/listings.json
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "data: scrape $(date -u +'%Y-%m-%dT%H:%MZ')"
            # Rebase in case another run pushed between our checkout and commit
            git pull --rebase origin ${{ github.ref_name }} || true
            git push
          fi

      - name: Copy snapshot for dashboard
        if: github.event.inputs.dry_run != 'true'
        run: cp data/listings.json dashboard/listings.json

      - name: Upload Pages artifact
        if: github.event.inputs.dry_run != 'true'
        uses: actions/upload-pages-artifact@v3
        with:
          path: dashboard

  deploy-pages:
    needs: scrape
    if: github.event.inputs.dry_run != 'true'
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
