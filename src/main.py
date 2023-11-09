#!/usr/bin/env python
"""Модуль запуска приложения."""
import requests

import config
from category_parsing import (
    parse_category,
)
from product_parsing import (
    parse_product,
)
from trendyol.services import (
    Parser,
)


def main():

    # TODO: Создать класс "Parser" с приведенным ниже функционалом.
    products_url = config.mb_target_products_url
    products = requests.get(products_url).json()

    parser = Parser()

    print('Парсинг товаров...')
    for product in products:
        parser.parse_product_by_url(product.get('url'))
        parse_product(url=product.get('url'))

    categories_url = config.mb_target_categories_url
    categories = requests.get(categories_url).json()

    for category in categories:
        parse_category(url=category.get('url'))


if __name__ == '__main__':
    main()
