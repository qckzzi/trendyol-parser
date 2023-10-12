import json

import re
import requests

from core import config
from product_parsing.product_parsing import parse_product


def parse_category(url: str, headers: dict):
    response = requests.get(url, headers=headers)
    pattern = r'__SEARCH_APP_INITIAL_STATE__=(?P<json_data>.*?);window'
    match = re.search(pattern, response.text)

    if match:
        raw_json = match.group('json_data')
        json_object = json.loads(raw_json)
        products = json_object.get('products')

        marketplace_url = config.get('trendyol', 'domain')

        for product in products:
            product_url = f'{marketplace_url}{product.get("url")}'
            parse_product(url=product_url, headers=headers)
