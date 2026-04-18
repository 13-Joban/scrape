import json
import os
import scrapy

from scraper.settings import TODAY
from scraper.spiders.myntra.base import MyntraBase
from scraper.items import PDPItem


class PdpSpider(MyntraBase):
    name = "pdp"

    custom_settings = {
        "ITEM_PIPELINES": {
            "scraper.pipelines.LocalDedupPipeline": 100,
            "scraper.pipelines.JsonPipeline": 200,
        }
    }
    path_filter = None

    def start_requests(self):
        # 1. Get dynamic context
        spider_date = getattr(self, 'date', TODAY)
        path_arg = getattr(self, 'path', None)

        # Parse the string argument into a Python list for comparison
        if path_arg and isinstance(path_arg, str) and path_arg.startswith("["):
            try:
                target_path = json.loads(path_arg)
            except json.JSONDecodeError:
                target_path = path_arg
        else:
            target_path = path_arg

        # 2. Locate the FIXED filename
        products_file = os.path.join(
            os.getcwd(), "data", self.retailer, spider_date, "products", "results.jsonl"
        )

        self.logger.info(f"Reading products from: {products_file}")

        if not os.path.exists(products_file):
            self.logger.error(f"File not found: {products_file}")
            return

        # 3. Read and Filter rows
        rows = []
        with open(products_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)

                # COMPARE LIST TO LIST
                # row.get("category") is now a list, target_path is now a list
                if target_path:
                    if row.get("category") == target_path:
                        rows.append(row)
                else:
                    rows.append(row)

        self.logger.info(f"Found {len(rows)} products matching path: {target_path}")


        for row in rows:
            url = row.get("pdp_url")
            if not url or not isinstance(url, str) or not url.startswith("http"):
                continue

            # USE STANDARD SCRAPY REQUEST TO BYPASS BASE CLASS BUGS
            yield scrapy.Request(
                url=url,
                headers=self.PDP_HEADERS,
                callback=self.parse_pdp,
                meta={"product_id": row.get("product_id"), "dont_filter": True,
                      "category": row.get("category")},
                priority=1
            )

    def parse_pdp(self, response):
        raw = response.xpath("//script[contains(text(), 'window.__myx =')]/text()").get("")

        if "window.__myx =" not in raw:
            self.logger.warning(f"window.__myx not found: {response.url}")
            return

        try:
            # Cleaner split to handle potential trailing garbage
            json_str = raw.split("window.__myx =", 1)[1].strip()
            if json_str.endswith(";"):
                json_str = json_str[:-1]

            data = json.loads(json_str)
        except (json.JSONDecodeError, IndexError) as e:
            self.logger.error(f"JSON parse failed {response.url}: {e}")
            return

        pdp = data.get("pdpData", {})
        if not pdp:
            self.logger.warning(f"No pdpData in JSON for {response.url}")
            return

        media_block = pdp.get("media", {})

        brand_block = pdp.get("brand", {})
        video_list = []
        # Myntra's Brightcove Account ID is usually constant
        account_id = "1830421494001"

        for video in media_block.get("videos", []):
            v_id = video.get("url") or video.get("id")
            host = video.get("host", "")

            if v_id and "Brightcove" in host:
                # Constructing a standard Brightcove web player link
                # Format: https://players.brightcove.net/{account_id}/default_default/index.html?videoId={video_id}
                playable_url = f"https://players.brightcove.net/{account_id}/default_default/index.html?videoId={v_id}"
                video_list.append(playable_url)
            elif v_id:
                video_list.append(v_id)

        all_images = []
        for album in media_block.get("albums", []):
            for img in album.get("images", []):
                src = img.get("imageURL", "")
                if src:
                    all_images.append(src)

        primary_image = all_images[0] if all_images else ""

        product_details = pdp.get("productDetails", [])

        description_text = ""
        features = []
        style_attrs = {}

        for detail in product_details:
            title = detail.get("title", "").strip()
            content = detail.get("description", "")
            if title == "Product Details":
                description_text = "".join(scrapy.Selector(text=content).xpath("//text()").getall()).strip()

                # 2. Extract <li> into features
                features = scrapy.Selector(text=content).xpath("//li//text()").getall()
                features = [f.strip() for f in features]
            elif title:

                clean_val = "".join(scrapy.Selector(text=content).xpath("//text()").getall()).strip()
                style_attrs[title] = clean_val

        for k, v in pdp.get("articleAttributes", {}).items():
            if k and v:
                style_attrs[k] = v

        current_id = str(response.meta.get("product_id") or pdp.get("id", ""))

        breadcrumbs = []

        # Target specifically application/ld+json with BreadcrumbList
        for script in response.xpath("//script[@type='application/ld+json']/text()").getall():
            try:
                ld = json.loads(script)
            except json.JSONDecodeError:
                continue

            # Could be a list of ld+json blocks or single dict
            if isinstance(ld, list):
                ld_items = ld
            else:
                ld_items = [ld]

            for item in ld_items:
                if item.get("@type") != "BreadcrumbList":
                    continue

                for element in item.get("itemListElement", []):
                    name = element.get("item", {}).get("name", "")
                    url = element.get("item", {}).get("@id", "")
                    position = element.get("position")

                    if name:
                        breadcrumbs.append({
                            "name": name,
                            "url": url,
                            "position": position,
                        })

                break

        yield PDPItem(
            url=response.url,
            product_id=current_id,
            name=pdp.get("name", ""),
            brand=brand_block.get("name", "") if isinstance(brand_block, dict) else "",
            mrp=float(pdp.get("price").get("mrp", 0)),
            selling_price=float(pdp.get("price").get("discounted", 0)) if pdp.get("price").get("discounted",
                                                                                               0) else float(
                pdp.get("price").get("mrp", 0)),
            features=features,
            category=response.meta.get("category"),
            style_attrs=style_attrs,
            primary_image=primary_image,
            all_images=all_images,
            videos=video_list,
            color=pdp.get("baseColour", ""),
            description=description_text or "",
        )

        # 5. Fixed variants URL building
        for colour in pdp.get("colours", []) or []:
            style_id = str(colour.get("styleId", ""))
            c_url = colour.get("url")
            if not style_id or style_id == current_id or not c_url:
                continue

            yield self._req(
                "https://www.myntra.com/" + c_url.lstrip("/"),
                callback=self.parse_pdp,
                meta={"product_id": style_id, "category": response.meta.get("category")},
                priority=1,
            )
