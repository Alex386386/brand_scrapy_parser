import scrapy


class ProductInfoParserItem(scrapy.Item):
    timestamp = scrapy.Field()
    rpc = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    discount = scrapy.Field()
    brand = scrapy.Field()
    section = scrapy.Field()
    price_data = scrapy.Field()
    stock = scrapy.Field()
    asset = scrapy.Field()
    metadata = scrapy.Field()
    variants = scrapy.Field()
