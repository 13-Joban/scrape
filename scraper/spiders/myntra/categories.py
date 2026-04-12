import json
from urllib.parse import quote

from scraper.settings import get_data_dirs
from scraper.spiders.myntra.base import MyntraBase
from scraper.items import CategoryItem


class CategoriesSpider(MyntraBase):
    name = "myntra_categories"

    paths = get_data_dirs("myntra")

    custom_settings = {
        "ITEM_PIPELINES": {},
        "FEEDS": {
            paths["CATEGORIES_FILE"]: {"format": "jsonlines"},
        },
    }
    def start_requests(self):
        yield self._req(
            "https://www.myntra.com/",
            callback=self.parse,
            meta={},
        )

    def parse(self, response):
        navs = response.xpath("//div[contains(@class, 'desktop-navContent')]")
        for nav in navs:
            top_name = nav.xpath(".//a[@data-type='navElements']/@data-group").get("").strip()
            top_url = "https://www.myntra.com" + nav.xpath(".//a[@data-type='navElements']/@href").get("")

            if not top_name:
                continue

            path = [top_name.lower()]
            categories = nav.xpath(
                ".//ul[contains(@class, 'desktop-navBlock')]"
                "/li/a[contains(@class, 'desktop-categoryLink')]"
            )

            if not categories:
                # no subcategories — this IS the leaf, yield it
                yield CategoryItem(url=top_url, path=path)
                return

            for cat in categories:
                cat_url = "https://www.myntra.com" + cat.xpath("./@href").get("")
                cat_name = cat.xpath(".//text()").get("").strip()
                yield CategoryItem(url=cat_url, path=path + [cat_name.lower()])
    #
    # def parse_sub(self, response):
    #     path = response.meta["path"]
    #     top_url = response.meta["top_url"]
    #     with open('r.html', 'w' ) as f:
    #         f.write(response.text)
    #
    #     categories = response.xpath(
    #             "//ul[contains(@class, 'categories-list')]//li//input/@value"
    #         ).getall()
    #     print(categories)
    #
    #     if not categories:
    #         print(top_url, path)
    #         # no subcategories — this IS the leaf, yield it
    #         yield CategoryItem(url=response.url, path=path)
    #         return
    #
    #     for cat_name in categories:
    #         sub_url = top_url + f"?f=Categories={quote(cat_name)}"
    #         yield CategoryItem(url=sub_url, path=path + [cat_name])