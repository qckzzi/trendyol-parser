import json
import re

import requests

import config
from product_parsing import (
    parse_product,
)
from trendyol.services import (
    Parser,
)


def parse_category(url: str):
    response = requests.get(url)
    pattern = r'__SEARCH_APP_INITIAL_STATE__=(?P<json_data>.*?);window'
    match = re.search(pattern, response.text)

    if match:
        raw_json = match.group('json_data')
        json_object = json.loads(raw_json)
        products = json_object.get('products')

        marketplace_url = config.trendyol_domain

        parser = Parser()

        for product in products:
            product_url = f'{marketplace_url}{product.get("url")}'
            parser.parse_product_by_url(product_url)
