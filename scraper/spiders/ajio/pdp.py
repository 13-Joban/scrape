"""
scrapy crawl ajio_pdp
scrapy crawl ajio_pdp -a path="Men - Kurtas"
"""

import json
import os
import re

import scrapy
from curl_cffi import requests as cffi_requests
from scrapy import Selector

from scraper.settings import get_data_dirs, TODAY
from scraper.spiders.ajio.base import AjioBase
from scraper.items import PDPItem


class AjioPdpSpider(AjioBase):
    name = "ajio_pdp"

    custom_settings = {
        **get_data_dirs("ajio"),
        "ITEM_PIPELINES": {
            "scraper.pipelines.LocalDedupPipeline": 100,
            "scraper.pipelines.JsonPipeline": 200,
        }
    }

    def __init__(self, path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_filter = path

    def start_requests(self):
        spider_date = getattr(self, 'date', TODAY)

        products_file = os.path.join(
            os.getcwd(), "data", self.retailer, spider_date, "products", "results.jsonl"
        )

        self.logger.info(f"Reading products from: {products_file}")

        if not os.path.exists(products_file):
            self.logger.error(f"File not found: {products_file}")
            return

        rows = []
        with open(products_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                if self.path_filter:
                    if row.get("category") == self.path_filter:
                        rows.append(row)
                else:
                    rows.append(row)

        self.logger.info(f"Found {len(rows)} products for path: {self.path_filter}")

        for row in rows:
            sku = row.get("product_id", "")
            if not sku:
                continue

            # AJIO PDP API endpoint
            api_url = f"https://www.ajio.com/api/p/{sku}"

            yield scrapy.Request(
                url=api_url,
                callback=self.parse_pdp,
                meta={
                    "product_id": sku,
                    "category": row.get("category"),
                    "dont_filter": True,
                }
            )

    def parse_pdp(self, response):

        pdp = json.loads(response.text)



        current_sku = response.meta.get("product_id", "")
        category = response.meta.get("category", "")

        # ── Images ──────────────────────────────────────────────
        # Keep only format="product", dedupe by galleryIndex
        seen_gallery = set()
        all_images = []
        for img in pdp.get("images", []):
            if img.get("format") == "product":
                idx = img.get("galleryIndex", 0)
                if idx not in seen_gallery:
                    seen_gallery.add(idx)
                    all_images.append(img.get("url", ""))

        primary_image = all_images[0] if all_images else ""

        # ── Pricing ─────────────────────────────────────────────
        price_block = pdp.get("price", {})
        was_price_block = pdp.get("wasPriceData", {})
        selling_price = float(price_block.get("value", 0))
        mrp = float(was_price_block.get("value", selling_price))
        discount_percent = price_block.get("discountPercent", "")

        # ── Feature attributes ──────────────────────────────────
        # featureData: [{name: "Fabric", featureValues: [{value: "Cotton"}]}]
        style_attrs = {}
        for feat in pdp.get("featureData", []):
            name = feat.get("name", "").strip()
            values = feat.get("featureValues", [])
            if name and values:
                style_attrs[name] = values[0].get("value", "")

        # ── Sizes (variantOptions) ───────────────────────────────
        sizes = []
        for variant in pdp.get("variantOptions", []):
            size_info = {}
            qualifiers = {
                q["qualifier"]: q["value"]
                for q in variant.get("variantOptionQualifiers", [])
                if q.get("value")
            }
            size_info["size"] = qualifiers.get("size", "")
            size_info["standard_size"] = qualifiers.get("standardSize", "")
            size_info["ean"] = qualifiers.get("ean", "")
            size_info["stock_status"] = variant.get("stock", {}).get("stockLevelStatus", "")
            size_info["stock_level"] = variant.get("stock", {}).get("stockLevel", 0)
            size_info["price"] = float(variant.get("priceData", {}).get("value", selling_price))
            size_info["sku_code"] = variant.get("code", "")
            sizes.append(size_info)

        # ── Color variants (other colors from baseOptions) ───────
        color_variants = []
        for opt in pdp.get("baseOptions", [{}])[0].get("options", []):
            color_sku = opt.get("code", "")
            color_url = opt.get("url", "")  # e.g. /slug/p/443380565_khaki
            color_val = None
            for q in opt.get("variantOptionQualifiers", []):
                if q.get("qualifier") == "color":
                    color_val = q.get("value")
            color_variants.append({
                "sku": color_sku,
                "color": color_val,
                "url": color_url,
            })

        # ── Ratings ──────────────────────────────────────────────
        ratings_block = pdp.get("ratingsResponse", {})
        agg = ratings_block.get("aggregateRating", {})
        ratings = {
            "average": agg.get("averageRating"),
            "count": agg.get("numUserRatings"),
        } if agg else {}

        # ── Breadcrumb path ──────────────────────────────────────
        breadcrumb_raw = (
            pdp.get("rilfnlBreadCrumbList", {})
            .get("rilfnlBreadCrumb", [])
        )
        breadcrumbs = [
            bc.get("name", "")
            for bc in breadcrumb_raw
            if bc.get("name")
        ]

        # ── Yield main item ──────────────────────────────────────
        yield PDPItem(
            url=f"https://www.ajio.com{pdp.get('url')}",
            product_id=current_sku,
            name=pdp.get("name", ""),
            brand=pdp.get("brandName", ""),
            mrp=mrp,
            selling_price=selling_price,
            features=[],                        # AJIO doesn't have bullet features like Myntra
            category=category,
            style_attrs=style_attrs,
            primary_image=primary_image,
            all_images=all_images,
            videos=[],
            color=pdp.get("verticalColor", ""),
            description=pdp.get("description", "") or pdp.get("summary", ""),
            breadcrumbs=breadcrumbs
        )

        # ── Crawl other color variants ───────────────────────────
        for cv in color_variants:
            cv_sku = cv["sku"]
            if not cv_sku or cv_sku == current_sku:
                continue

            api_url = f"https://www.ajio.com/api/p/{cv_sku}"
            yield scrapy.Request(
                url=api_url,
                callback=self.parse_pdp,
                meta={
                    "product_id": cv_sku,
                    "category": category,
                    "dont_filter": True,
                }
            )