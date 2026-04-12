import os
import json
import logging
from scraper.items import ProductListItem, PDPItem
from scraper.settings import get_data_dirs

class JsonPipeline:
    """Writes items immediately to JSONL in the retailer/date directory."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        # 1. Use your settings function to get the correct paths
        retailer = getattr(spider, 'retailer', 'unknown')
        dirs = get_data_dirs(retailer)

        # Mapping for easy access in process_item
        self.paths = {
            "products": dirs["PRODUCTS_DIR"],
            "pdp": dirs["PDP_DIR"],
        }

    def process_item(self, item, spider):
        # 2. Determine if it's a product or a pdp
        kind = "products" if isinstance(item, ProductListItem) else "pdp"
        target_dir = self.paths.get(kind)

        # 3. FIXED FILENAME: results.jsonl (No category in filename)
        file_path = os.path.join(target_dir, "results.jsonl")

        # 4. Write immediately (No complex buffering)
        try:
            with open(file_path, "a+", encoding="utf-8") as f:
                # Convert item to dict and dump as one line
                line = json.dumps(dict(item), ensure_ascii=False) + "\n"
                f.write(line)
        except Exception as e:
            self.logger.error(f"Failed to write to {file_path}: {e}")

        return item

# ─── Local dedup remains the same (important for PDP spider) ──────────────────

class LocalDedupPipeline:
    def __init__(self):
        self.seen_ids = set()

    def process_item(self, item, spider):
        if not isinstance(item, PDPItem):
            return item

        pid = str(item.get("product_id", ""))
        if not pid:
            return item

        if pid in self.seen_ids:
            from scrapy.exceptions import DropItem
            raise DropItem(f"Duplicate found: {pid}")

        self.seen_ids.add(pid)
        return item