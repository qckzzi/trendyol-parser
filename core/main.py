#!/usr/bin/env python
"""Модуль запуска приложения."""
from category_parsing.category_parsing import parse_category
from core import config
from product_parsing.product_parsing import parse_product
import requests

def main():

    #TODO: Создать класс "Parser" с приведенным ниже функционалом.
    headers = {'User-Agent': config.get('request', 'user_agent')}
    products_url = config.get('markets_bridge', 'target_products_url')
    products = requests.get(products_url).json()

    for product in products:
        parse_product(url=product.get('url'), headers=headers)

    categories_url = config.get('markets_bridge', 'target_categories_url')
    categories = requests.get(categories_url).json()

    for category in categories:
        parse_category(url=category.get('url'), headers=headers)


if __name__ == '__main__':
    main()
