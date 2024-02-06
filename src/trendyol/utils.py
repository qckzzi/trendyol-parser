import json
import re
from math import (
    ceil,
)
from urllib.parse import (
    urlparse,
)

import requests

import config
from trendyol.dtos import (
    TrendyolAttributeDTO,
    TrendyolAttributeValueDTO,
    TrendyolBrandDTO,
    TrendyolCategoryDTO,
    TrendyolProductDTO,
)
from trendyol.exceptions import (
    NotFoundDataError,
)


class Parser:
    """Trendyol information parser."""

    product_data_class = TrendyolProductDTO
    category_data_class = TrendyolCategoryDTO
    attribute_data_class = TrendyolAttributeDTO
    attribute_value_data_class = TrendyolAttributeValueDTO
    brand_data_class = TrendyolBrandDTO

    product_re_pattern = r'__PRODUCT_DETAIL_APP_INITIAL_STATE__\s*=\s*(?P<json_data>.*?);\s*window'
    category_re_pattern = r'__SEARCH_APP_INITIAL_STATE__\s*=\s*(?P<json_data>.*?);\s*window'

    @classmethod
    def parse_product_urls_by_category_url(cls, url: str) -> list[str]:
        category = cls.parse_category_by_url(url)

        products = category['products']
        pages_count = ceil(category['totalCount'] / category['configuration']['searchPageItemCount'])

        for page in range(2, pages_count+1):
            category = cls.parse_category_by_url(url, page=page)
            products.extend(category['products'])

        marketplace_url = config.trendyol_domain

        return [f'{marketplace_url}{product["url"]}' for product in products]

    @classmethod
    def parse_category_by_url(cls, url: str, page: int = None) -> dict:
        request_params = {'pi': page} if page else {}

        response = requests.get(url, params=request_params)
        response.raise_for_status()

        match = re.search(cls.category_re_pattern, response.text)

        if not match:
            raise NotFoundDataError(f'Category at url {url} not found.')

        raw_json = match.group('json_data')

        return json.loads(raw_json)

    # TODO: DRY
    @classmethod
    def parse_product_urls_by_product_card_url(cls, url: str) -> list[str]:
        response = requests.get(url)
        match = re.search(cls.product_re_pattern, response.text)

        if not match:
            raise NotFoundDataError(f'Product at url {url} not found.')

        raw_json = match.group('json_data')
        json_object = json.loads(raw_json)
        raw_product = json_object.get('product')
        product_group_response = requests.get(f'{config.trendyol_product_group_url}{raw_product["productGroupId"]}')

        product_urls = []

        slicing_attributes = product_group_response.json()['result']['slicingAttributes']

        url_query = urlparse(url).query

        for slicing_attribute in slicing_attributes:
            for attribute in slicing_attribute['attributes']:
                for attribute_content in attribute['contents']:
                    product_url = f'{config.trendyol_domain}{attribute_content["url"]}?{url_query}'
                    product_urls.append(product_url)

        return product_urls

    # TODO: Декомпозировать метод
    @classmethod
    def parse_product_by_url(cls, url: str) -> product_data_class:
        response = requests.get(url)
        match = re.search(cls.product_re_pattern, response.text)

        if not match:
            for _ in range(3):
                response = requests.get(url)
                match = re.search(cls.product_re_pattern, response.text)

                if match:
                    break
            else:
                raise NotFoundDataError(f'Product at url {url} not found.')

        raw_json = match.group('json_data')
        json_object = json.loads(raw_json)
        raw_product = json_object.get('product')

        if len(raw_product['allVariants']) > 1:
            raise NotImplementedError('Loading of products with multiple variants is not implemented.')

        raw_category = raw_product['category']

        category_kwargs = dict(
            id=raw_category['id'],
            name=raw_category['name'],
        )

        category = cls.category_data_class(**category_kwargs)

        raw_brand = raw_product['brand']

        brand_kwargs = dict(
            id=raw_brand['id'],
            name=raw_brand['name'],
            path=raw_brand['path'],
        )

        brand = cls.brand_data_class(**brand_kwargs)

        merchant_id = raw_product['merchant']['id']

        for listing in raw_product['merchantListings']:
            if listing['merchant']['id'] == merchant_id:
                stock_quantity = listing['variants'][0]['quantity']
                break
        else:
            stock_quantity = 0

        attribute_values = []

        raw_attributes = raw_product['attributes']

        for raw_attribute in raw_attributes:
            attribute_kwargs = dict(
                id=raw_attribute['key']['id'],
                name=raw_attribute['key']['name'],
            )
            attribute = cls.attribute_data_class(**attribute_kwargs)

            attribute_value_kwargs = dict(
                id=raw_attribute['value']['id'],
                value=raw_attribute['value']['name'],
                attribute=attribute,
            )
            attribute_value = cls.attribute_value_data_class(**attribute_value_kwargs)
            attribute_values.append(attribute_value)

        image_urls = [f'{config.trendyol_images_domain}{image_url}' for image_url in raw_product['images']]

        product = cls.product_data_class(
            id=raw_product['id'],
            name=raw_product['name'],
            url=url,
            category=category,
            brand=brand,
            item_number=raw_product['variants'][0]['itemNumber'],
            stock_quantity=stock_quantity,
            price=raw_product['variants'][0]['price']['originalPrice']['value'],
            discounted_price=raw_product['variants'][0]['price']['discountedPrice']['value'],
            product_group_id=raw_product['productGroupId'],
            product_code=raw_product['productCode'],
            values=attribute_values,
            image_urls=image_urls,
        )

        return product
