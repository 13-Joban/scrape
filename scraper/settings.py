BOT_NAME = "scraper"
SPIDER_MODULES = ["scraper.spiders.myntra", "scraper.spiders.ajio"]

# ── Politeness ────────────────────────────────────────────────────────────────
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# ── Output dirs ───────────────────────────────────────────────────────────────
# settings.py
from datetime import date
import os

# Get the absolute path to the project root (where scrapy.cfg lives)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = date.today().isoformat()  # 2026-04-04


def get_data_dirs(retailer):
    # This creates a clean structure: data/myntra/2026-04-04/
    base = os.path.join(BASE_DIR, "data", retailer, TODAY)

    # Ensure directories exist
    os.makedirs(os.path.join(base, "products"), exist_ok=True)
    os.makedirs(os.path.join(base, "pdp"), exist_ok=True)

    return {
        "PRODUCTS_DIR": os.path.join(base, "products"),
        "PDP_DIR": os.path.join(base, "pdp"),
        "CATEGORIES_FILE": os.path.join(base, "categories.json"),
    }


# ── Pipelines ─────────────────────────────────────────────────────────────────
# settings.py OR pdp.py custom_settings
ITEM_PIPELINES = {
    "scraper.pipelines.JsonPipeline": 100,
    "scraper.pipelines.ParquetPipeline": 200,
}

# ── Feeds (categories written as jsonlines — tiny, no parquet overhead) ───────
# Handled manually in the pipeline for full control.

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json, text/html",
    "Accept-Language": "en-US,en;q=0.9",
}

DOWNLOADER_MIDDLEWARES = {
    'scraper.middlewares.CurlCffiMiddleware': 543,
}