import json
import os
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from twisted.python.failure import Failure

from maksavit_parser.items import ProductInfoParserItem
from maksavit_parser.settings import PRODUCT_SPIDER_NAME
from maksavit_parser.utils import (
    get_the_price,
    get_the_common_data,
    get_the_image,
    get_the_status,
    CATEGORY_ERROR,
)

chrome_options = Options()
chrome_options.add_experimental_option('prefs', {
    'profile.default_content_setting_values.notifications': 2
})

current_dir = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = os.path.join(current_dir, 'chromedriver')
chrome_options.binary_location = chromedriver_path


class ProductInfoSpider(scrapy.Spider):
    name = PRODUCT_SPIDER_NAME

    def __init__(self, categories: str = '', *args, **kwargs):
        super(ProductInfoSpider, self).__init__(*args, **kwargs)
        self.categories = categories.split(';')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.cookies = {}

    def start_requests(self) -> Any:
        with open('maksavit_parser/categories.json', 'r', encoding='utf-8') as file:
            all_categories = json.load(file)

        for category in self.categories:
            url = all_categories.get(category.strip().lower())
            if url:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_category,
                    meta={'driver': self.driver}
                )
            else:
                print(CATEGORY_ERROR)

    def parse_category(self, response: scrapy.http.Response) -> Any:

        if not self.cookies:
            self.driver.get(response.url)
            wait = WebDriverWait(self.driver, 10)
            confirmation_button = wait.until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, '.button.button--red.city-btn'))
            )
            confirmation_button.click()
            wait.until_not(
                ec.presence_of_element_located((By.CSS_SELECTOR, '.base-modal__main'))
            )
            full_cookies = self.driver.get_cookies()
            self.cookies = {cookie['name']: cookie['value'] for cookie in full_cookies}

        for product_link in response.css('a.preview-img-wrapper::attr(href)'):
            category_name = response.css(
                'li.breadcrumbs__item:nth-last-child(2) span[itemprop="name"]::text').get().strip()
            product_type = response.css(
                'li.breadcrumbs__item:last-child span[itemprop="name"]::text').get().strip()
            yield response.follow(
                product_link,
                self.parse_product,
                meta={'category_name': category_name, 'product_type': product_type},
                cookies=self.cookies
            )

        current_page_number = int(response.meta.get('page_number', 1))
        next_page_number = current_page_number + 1
        base_url = response.url.split('?')[0]
        next_page_url = urljoin(base_url, f'?page={next_page_number}')

        yield response.follow(
            next_page_url,
            self.parse_category,
            meta={'page_number': next_page_number},
            errback=self.handle_404,
        )

    def handle_404(self, failure: Failure) -> None:
        if failure.value.response.status == 404:
            return

    def parse_product(self, response: scrapy.http.Response) -> Any:
        timestamp = int(datetime.now().timestamp())  # время получения продукта
        rpc = str(response.url).split('/')[-2]  # код продукта
        product_url = response.url  # юрл продукта
        product_title = response.css('h1.product-top__title::text').get()  # название

        category_name = response.meta.get('category_name')  # иерархия разделов
        product_type = response.meta.get('product_type')

        brand = response.css('a.product-info__brand-value::text').get()  # брэнд товара
        if not brand:
            brand = 'Товар без бренда.'

        product_data = get_the_common_data(response)  # получить информацию о товаре

        quantity_items_wrapper = response.css('div.quantity-items-wrapper')  # количество вариантов
        if quantity_items_wrapper:
            count = len(quantity_items_wrapper.css(':scope > div'))
        else:
            count = 1

        full_image_url = get_the_image(response)  # ссылка на изображение

        status, combined_text = get_the_status(response)  # статус наличия

        auction_div = response.css('div.product-auctions')  # наличие акции
        discount_flag = False
        if auction_div:
            discount_flag = True

        price_data = get_the_price(response, discount_flag, combined_text, product_title)  # данные о цене

        data = {
            'timestamp': timestamp,
            'rpc': rpc,
            'url': product_url,
            'title': product_title.strip(),
            'discount': discount_flag,
            'brand': brand.strip(),
            'section': [category_name, product_type],
            'price_data': price_data,
            'stock': status,
            'asset': full_image_url,
            'metadata': product_data,
            'variants': count,
        }
        yield ProductInfoParserItem(data)
