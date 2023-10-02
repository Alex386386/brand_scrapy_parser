import json
import os
from typing import Any

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from maksavit_parser.settings import (
    CATEGORY_SPIDER_NAME,
    CATEGORY_ALLOWED_DOMAINS,
    CATEGORY_START_URLS,
)

chrome_options = Options()
chrome_options.add_experimental_option('prefs', {
    'profile.default_content_setting_values.notifications': 2
})

current_dir = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = os.path.join(current_dir, 'chromedriver')
chrome_options.binary_location = chromedriver_path


class CategorySpider(scrapy.Spider):
    name = CATEGORY_SPIDER_NAME
    allowed_domains = CATEGORY_ALLOWED_DOMAINS
    start_urls = CATEGORY_START_URLS

    def __init__(self, *args, **kwargs):
        super(CategorySpider, self).__init__(*args, **kwargs)
        self.links = dict()
        self.driver = webdriver.Chrome(options=chrome_options)

    def start_requests(self) -> Any:
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, meta={'driver': self.driver})

    def parse(self, response: scrapy.http.Response) -> Any:
        self.driver.get(response.url)
        modal_close_button = WebDriverWait(self.driver, 5).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, '.base-modal__btn-close'))
        )
        modal_close_button.click()
        WebDriverWait(self.driver, 1).until_not(
            ec.presence_of_element_located((By.CSS_SELECTOR, '.base-modal__main'))
        )

        accordions = self.driver.find_elements(By.CSS_SELECTOR, 'li.accordion__item .accordion__arrow-wrap')
        for accordion in tqdm(accordions):
            self.driver.execute_script('arguments[0].click();', accordion)
            items = self.driver.find_elements(By.CSS_SELECTOR, '.accordion__content .catalog-category__item a')
            for item in items:
                link = item.get_attribute('href')
                title = item.text.strip().lower()
                self.links[title] = link

    def close(self, reason) -> None:
        with open('maksavit_parser/categories.json', 'w', encoding='utf-8') as write_file:
            json.dump(self.links, write_file, ensure_ascii=False, indent=2)
        self.driver.quit()
