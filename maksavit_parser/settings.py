BOT_NAME = 'maksavit_parser'
LOG_LEVEL = 'ERROR'

CATEGORY_SPIDER_NAME = 'category'
PRODUCT_SPIDER_NAME = 'product_info_spider'

SPIDER_MODULES = ['maksavit_parser.spiders']
NEWSPIDER_MODULE = 'maksavit_parser.spiders'
CATEGORY_ALLOWED_DOMAINS = ['maksavit.ru']
CATEGORY_START_URLS = ['https://maksavit.ru/novosibirsk/catalog/']
ROBOTSTXT_OBEY = True
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
FEED_EXPORT_ENCODING = 'utf-8'

ITEM_PIPELINES = {
    'maksavit_parser.pipelines.ProductInfoPipeline': 200,
}
