"""
scrapy crawl ajio_products
scrapy crawl ajio_products -a path="Men > Topwear > Kurtas"
"""

import json
from urllib.parse import urlparse, parse_qs

import requests as req_lib
import scrapy

from scraper.settings import get_data_dirs
from scraper.spiders.ajio.base import AjioBase
from scraper.items import ProductListItem


class ProductsSpider(AjioBase):
    name = "ajio_products"

    custom_settings = {
        **get_data_dirs("ajio"),
        "ITEM_PIPELINES": {
            "scraper.pipelines.JsonPipeline": 100,
        }
    }
    path_filter = None

    def __init__(self, path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if path:
            try:
                self.path_filter = json.loads(path)
            except (json.JSONDecodeError, TypeError):
                self.path_filter = path

    def _build_api_url(self, category_id, query_param, category_name, page=0):
        params = {
            "fields": "SITE",
            "currentPage": page,
            "pageSize": 45,
            "format": "json",
            "query": query_param,
            "gridColumns": 3,
            "facets": f"l1l3nestedcategory:{category_name}",
            "advfilter": "true",
            "platform": "Desktop",
        }
        prepared = req_lib.Request(
            "GET",
            f"https://www.ajio.com/api/category/{category_id}",
            params=params,
        ).prepare()
        return prepared.url

    def start_requests(self):
        with open('/home/jobanpreetsingh/scraper/men_filters.json') as f:
            men_filters = json.load(f)

        with open('/home/jobanpreetsingh/scraper/women_filters.json') as f:
            women_filters = json.load(f)

        all_values = []
        for filters in [men_filters, women_filters][:3]:
            for f in filters:
                if f.get("code") == 'l1l3nestedcategory':
                    all_values.extend(f.get('values', []))
                    break

        for entry in all_values:
            web_url = "https://www.ajio.com" + entry['query']['url']
            category_name = entry['code']

            path_parts = urlparse(web_url).path.split('/')
            category_id = path_parts[-1]

            query_param = parse_qs(urlparse(web_url).query).get('q', [''])[0]
            query_param = query_param.replace('genderfilter:Men', '').replace('genderfilter:Women', '')
            query_param = query_param.replace('::', ':').lstrip(':')

            api_url = self._build_api_url(category_id, query_param, category_name, page=0)

            yield scrapy.Request(
                url=api_url,
                callback=self.parse_products,
                meta={
                    "category_id": category_id,
                    "category_name": category_name,
                    "query_param": query_param,
                    "page": 0,
                }
            )

    def parse_products(self, response):
        meta = response.meta
        page = meta["page"]

        try:
            data = response.json()
        except Exception as e:
            self.logger.error(f"JSON parse failed on {response.url}: {e}")
            return

        if isinstance(data, list):
            payload = data[0]
        else:
            payload = data

        products = payload.get("products", [])
        pagination = payload.get("pagination", {})

        current_page = pagination.get("currentPage", page)
        total_pages = pagination.get("totalPages", 1)
        page_size = pagination.get("pageSize", 45)

        for position, product in enumerate(products, start=current_page * page_size + 1):
            raw_url = product.get("url", "")
            sku = raw_url.split("/p/")[-1] if "/p/" in raw_url else ""
            if not sku:
                continue

            yield ProductListItem(
                category_url=f"https://www.ajio.com/api/category/{meta['category_id']}",
                category=meta["category_name"],
                page=current_page,
                position=position,
                pdp_url=f"https://www.ajio.com/p/{sku}",
                product_id=sku,
            )

        # Pagination
        next_page = current_page + 1
        if next_page < total_pages:
            api_url = self._build_api_url(
                meta["category_id"],
                meta["query_param"],
                meta["category_name"],
                page=next_page,
            )
            yield scrapy.Request(
                url=api_url,
                callback=self.parse_products,
                meta={**meta, "page": next_page},
            )