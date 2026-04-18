import scrapy


class CategoryItem(scrapy.Item):
    url = scrapy.Field()
    path = scrapy.Field()  # e.g. ["Drinks", "Spirits", "Vodka"]


class ProductListItem(scrapy.Item):
    category_url = scrapy.Field()
    page = scrapy.Field()
    position = scrapy.Field()
    pdp_url = scrapy.Field()
    category = scrapy.Field()
    product_id = scrapy.Field()  # whatever ID is on the listing page
    breadcrumbs = scrapy.Field()


class PDPItem(scrapy.Item):
    url = scrapy.Field()
    product_id = scrapy.Field()
    category = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    features = scrapy.Field()  # list[str]
    style_attrs = scrapy.Field()  # dict  e.g. {"Color": "Red", "Size": "M"}
    primary_image = scrapy.Field()  # str URL
    all_images = scrapy.Field()  # list[str]
    videos = scrapy.Field()  # list[str]
    description = scrapy.Field()
    mrp = scrapy.Field()
    selling_price = scrapy.Field()
    color = scrapy.Field()
    breadcrumbs = scrapy.Field()
