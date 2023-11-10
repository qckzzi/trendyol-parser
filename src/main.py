#!/usr/bin/env python
import logging

import requests

import config
from markets_bridge.services import (
    Formatter,
    Sender,
)
from trendyol.services import (
    Parser,
)


def main():
    # TODO: Получать урлы из очереди, а не забирать запросом самостоятельно

    target_products = requests.get(config.mb_target_products_url).json()

    for product in target_products:
        logging.info(f'Process product by url {product["url"]}...')

        try:
            product_processing(url=product['url'])
        except Exception as e:
            logging.exception(e)
        else:
            logging.info(f'Success!')

    target_categories = requests.get(config.mb_target_categories_url).json()
    
    for category in target_categories:
        logging.info(f'Process category by url {category["url"]}...')

        try:
            category_processing(url=category['url'])
        except Exception as e:
            logging.exception(e)
        else:
            logging.info(f'Success!')


def category_processing(url: str):
    product_url_list = Parser.parse_product_urls_by_category_url(url)

    for product_url in product_url_list:
        product_processing(product_url)


def product_processing(url: str):
    formatter = Formatter()

    trendyol_product = Parser.parse_product_by_url(url)
    formatter.trendyol_product = trendyol_product

    mb_category = formatter.get_category()
    Sender.send_category(mb_category)

    mb_characteristics = formatter.get_characteristics()
    for char in mb_characteristics:
        Sender.send_characteristic(char)

    mb_values = formatter.get_characteristic_values()
    for value in mb_values:
        Sender.send_characteristic_value(value)

    mb_brand = formatter.get_brand()
    Sender.send_brand(mb_brand)

    mb_product = formatter.get_product()
    existed_product_response = Sender.send_product(mb_product)

    if existed_product_response.status_code == 201:
        product = existed_product_response.json()
        for image_url in trendyol_product.image_urls:
            Sender.send_image(image_url, product['id'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s')

    try:
        main()
    except Exception as e:
        logging.exception(e)
