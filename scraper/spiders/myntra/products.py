
import json
import os

from scraper.settings import get_data_dirs
from scraper.spiders.myntra.base import MyntraBase
from scraper.items import ProductListItem


class ProductsSpider(MyntraBase):
    name = "myntra_products"

    custom_settings = {
        **get_data_dirs("myntra"),
        "ITEM_PIPELINES": {
            "scraper.pipelines.JsonPipeline": 100,
        }
    }
    # -a path="[Men, Topwear, Kurtas]"   (optional)
    path_filter = None

    def __init__(self, path=None, *args, **kwargs):
        super(ProductsSpider, self).__init__(*args, **kwargs)
        if path:
            try:
                # Converts the string '["men", "suits"]' to a real list
                self.path_filter = json.loads(path)
            except (json.JSONDecodeError, TypeError):
                self.path_filter = path

    def start_requests(self):
        cats_file = self.settings["CATEGORIES_FILE"]

        if not os.path.exists(cats_file):
            self.logger.error(f"categories.json not found at {cats_file}")
            return

        with open(cats_file) as f:
            categories = [json.loads(line) for line in f if line.strip()]

        if self.path_filter:
            categories = [c for c in categories if c["path"] == self.path_filter]

        for cat in categories:
            # We use the direct HTML URL from your categories.json
            base_url = cat["url"]

            # Simple p=1 for the first page
            join_char = "&" if "?" in base_url else "?"
            start_url = f"{base_url}{join_char}p=1"

            yield self._req(
                start_url,
                callback=self.parse_products,
                meta={
                    "category_url": base_url,
                    "path": cat["path"],
                    "page": 1,
                },
                api=False,  # We want the HTML page now
            )

    def parse_products(self, response):
        meta = response.meta
        page = meta["page"]

        # 1. Extract the JSON from the script tag using your split logic
        # We look for the line containing window.__myx
        try:
            raw_data = response.xpath("//script[contains(text(), 'window.__myx =')]/text()").get()
            if not raw_data:
                self.logger.error(f"Could not find window.__myx on {response.url}")
                return

            # Split and clean to get the valid JSON object
            json_str = raw_data.split("window.__myx =", 1)[1].strip()
            # Remove trailing semicolon if present
            if json_str.endswith(";"):
                json_str = json_str[:-1]

            data = json.loads(json_str)
            # Access searchData as seen in your JSON Editor screenshot
            search_data = data.get("searchData", {})
            results = search_data.get("results", {})
            products = results.get("products", [])
        except Exception as e:
            self.logger.error(f"JSON extraction failed: {e}")
            return

        # 2. Yield items
        rows = 50  # Myntra standard rows per page
        for position, product in enumerate(products, start=(page - 1) * rows + 1):
            yield ProductListItem(
                category_url=meta["category_url"],
                category=meta["path"],
                page=page,
                position=position,
                pdp_url="https://www.myntra.com/" + product.get("landingPageUrl", ""),
                product_id=str(product.get("productId", "")),
            )

        # 3. Pagination using p= query param
        total_count = results.get("totalCount", 0)
        if page * rows < total_count:
            next_page = page + 1
            base_url = meta["category_url"]
            join_char = "&" if "?" in base_url else "?"
            next_url = f"{base_url}{join_char}p={next_page}"

            yield self._req(
                next_url,
                callback=self.parse_products,
                meta={**meta, "page": next_page},
                priority=2,
                api=False,
            )