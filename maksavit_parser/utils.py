import re
from urllib.parse import urljoin

import scrapy

CATEGORY_ERROR: str = (
    'Данная категория отсутствует в с писке категорий.'
    ' Обновите список или проверьте правильность написания категории.'
)


def get_the_price(
        response: scrapy.http.Response,
        discount_flag: bool,
        combined_text: str,
        product_title: str,
) -> dict:
    match = re.search(r'(\d{1,9}(?:\s\d{3})*)(?=\s*₽)', combined_text)
    price_data = dict()
    if match:
        price = int(match.group(1).replace(' ', ''))
        if discount_flag:
            first_word_of_title = product_title.split()[0]
            pattern = r'Cкидка (\d{1,2}%) на ' + first_word_of_title
            auction_div = response.css('div.product-auctions *::text').getall()
            combined_text = ' '.join([tex.strip() for tex in auction_div])
            auction_match = re.search(pattern, combined_text)
            if auction_match:
                discount = auction_match.group(1)
                discounted_price = price - ((price * int(discount[:-1])) / 100)
                price_data['original'] = price
                price_data['discounted_price'] = int(discounted_price)
                price_data['discount'] = f'Скидка {discount}'
        else:
            price_data['original'] = price
    else:
        price_data['original'] = 'Последняя цена продажи недоступна'
    return price_data


def get_the_common_data(response: scrapy.http.Response) -> dict:
    sections = response.css('div.product-instruction__guide > div')
    product_data = {}
    for section in sections:
        title = section.css('h3.desc::text').get()
        texts = section.xpath(
            'h3/following-sibling::text() | h3/following-sibling::*[not(self::h3)]/descendant::text()'
        ).getall()
        text = ' '.join(t.strip() for t in texts if t.strip()).strip()
        if title:
            product_data[title] = text
    return product_data


def get_the_image(response: scrapy.http.Response) -> str:
    product_picture_div = response.css('div.product-picture')
    image_src = product_picture_div.css('img::attr(src)').get()
    if image_src and image_src.strip():
        base_url = response.url
        full_image_url = urljoin(base_url, image_src)
    else:
        full_image_url = 'Изображение отсутствует'
    return full_image_url


def get_the_status(response: scrapy.http.Response) -> tuple[str, str]:
    texts = response.css('div.price-box *::text').getall()
    combined_text = ' '.join([tex.strip() for tex in texts])
    if 'нет в наличии в вашем городе' in combined_text.lower():
        status = 'Нет в наличии'
    elif 'данный товар в настоящий момент отсутствует' in combined_text.lower():
        status = 'под заказ'
    else:
        status = 'в наличии'
    return status, combined_text
