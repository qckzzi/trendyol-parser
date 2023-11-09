import json
import re

import requests

import config
from trendyol.dtos import (
    AttributeDTO,
    AttributeValueDTO,
    BrandDTO,
    CategoryDTO,
    ProductDTO,
    ProductVariantDTO,
)
from trendyol.exceptions import (
    NotFoundDataError,
)


class Parser:
    """Product information parser."""

    product_data_class = ProductDTO
    category_data_class = CategoryDTO
    attribute_data_class = AttributeDTO
    attribute_value_data_class = AttributeValueDTO
    brand_data_class = BrandDTO
    variant_data_class = ProductVariantDTO

    product_re_pattern = r'__PRODUCT_DETAIL_APP_INITIAL_STATE__\s*=\s*(?P<json_data>.*?);\s*window'

    def parse_product_by_url(self, url: str) -> product_data_class:
        response = requests.get(url)
        match = re.search(self.product_re_pattern, response.text)

        if not match:
            raise NotFoundDataError(f'Product at url {url} not found.')

        raw_json = match.group('json_data')
        json_object = json.loads(raw_json)
        raw_product = json_object.get('product')

        raw_category = raw_product['category']

        category_kwargs = dict(
            id=raw_category['id'],
            name=raw_category['name'],
        )

        category = self.category_data_class(**category_kwargs)

        raw_brand = raw_product['brand']

        brand_kwargs = dict(
            id=raw_brand['id'],
            name=raw_brand['name'],
            path=raw_brand['path'],
        )

        brand = self.brand_data_class(**brand_kwargs)

        variants = []

        variant_attribute_kwargs = dict(
            id=raw_product['variants'][0]['attributeId'],
            name=raw_product['variants'][0]['attributeName'],
        )

        variant_attribute = self.attribute_data_class(**variant_attribute_kwargs)

        for raw_variant in raw_product['allVariants']:
            variant_value_kwargs = dict(
                id=0,
                value=raw_variant['value'],
                attribute=variant_attribute,
            )

            variant_value = self.attribute_value_data_class(**variant_value_kwargs)

            if raw_product['showVariants']:
                product_detail_url = f'{config.trendyol_product_detail_url}{raw_product['id']}'
                product_detail_response = requests.get(
                    product_detail_url,
                    params={'itemNumber': raw_variant['itemNumber']},
                )
                product_detail_json = product_detail_response.json()
                product_detail = product_detail_json['result']

                stock_quantity_enumerate = [
                    listing['variants'][0]['quantity'] for listing
                    in product_detail['merchantListings']
                ]
            else:
                stock_quantity_enumerate = [
                    listing['variants'][0]['quantity'] for listing
                    in raw_product['merchantListings']
                ]

            variant_kwargs = dict(
                item_number=raw_variant['itemNumber'],
                stock_quantity=sum(stock_quantity_enumerate),
                price=raw_variant['price'],
                value=variant_value,
            )

            variant = self.variant_data_class(**variant_kwargs)
            variants.append(variant)

        attribute_values = []

        raw_attributes = raw_product['attributes']

        for raw_attribute in raw_attributes:
            attribute_kwargs = dict(
                id=raw_attribute['key']['id'],
                name=raw_attribute['key']['name'],
            )
            attribute = self.attribute_data_class(**attribute_kwargs)

            attribute_value_kwargs = dict(
                id=raw_attribute['value']['id'],
                value=raw_attribute['value']['name'],
                attribute=attribute,
            )
            attribute_value = self.attribute_value_data_class(**attribute_value_kwargs)
            attribute_values.append(attribute_value)

        try:
            product_kwargs = dict(
                id=raw_product['id'],
                name=raw_product['name'],
                url=f'{config.trendyol_domain}{raw_product["url"]}',
                category=category,
                brand=brand,
                product_group_id=raw_product['productGroupId'],
                product_code=raw_product['productCode'],
                variants=variants,
                values=attribute_values,
            )
        except KeyError as e:
            raise KeyError(f'Possible change in product data sources. Error: {e}')

        product = self.product_data_class(**product_kwargs)

        return product


def unpack_attributes(attributes: list[dict], category_id: int) -> tuple[list[dict], list[dict]]:

    return processed_attributes, processed_attribute_values


def send_product(product):
    product_char_values = [attr.get('value', {}).get('id') for attr in product.get('attributes')]
    product_id = product.get('id')
    trendyol_host = config.trendyol_domain
    data = dict(
        external_id=product_id,
        name=product.get('name'),
        price=product.get('price', {}).get('sellingPrice', {}).get('value'),
        discounted_price=product.get('price', {}).get('discountedPrice', {}).get('value'),
        url=f'{trendyol_host}{product.get("url")}',
        category_external_id=product.get('originalCategory', {}).get('id'),
        characteristic_value_external_ids=product_char_values,
        marketplace_id=config.marketplace_id,
    )
    response = requests.post(
        config.mb_products_url,
        json=data,
    )
    if response.status_code == 201:
        print(f'Товар "{product.get("name")}" успешно создан')

        mb_product = response.json()

        for image_path in product.get('images'):
            content_url = config.trendyol_images_domain
            image_url = f'{content_url}{image_path}'
            parse_image(image_url, mb_product.get('id'))
    elif response.status_code == 200:
        print(f'Товар "{product.get("name")}" уже существует в системе')
    else:
        print(f'Ошибка создания товара "{product.get("name")}"\nSTATUS: {response.status_code}\n')


def parse_image(url, product_id):
    try:
        get_image_response = requests.get(url)

        with open('temp.jpg', 'wb') as file:
            file.write(get_image_response.content)
    except Exception as ex:
        print(f'Неполадки при загрузке изображения! Повторная попытка...\n({ex})\n')
        parse_image(url, product_id)

        return

    response = requests.post(
        config.mb_product_images_url,
        files=dict(image=open('temp.jpg', 'rb')),
        data=dict(product=product_id),
    )

    if response.status_code == 201:
        print(f'Изображение успешно создано.')
    else:
        print(f'Ошибка создания изображения\nSTATUS: {response.status_code}')


def send_attributes(attributes: list[dict]):
    print('Loading attributes to the server...')
    characteristics_url = config.mb_characteristics_url

    for attribute in attributes:
        response = requests.post(characteristics_url, json=attribute)

        if response.status_code == 201:
            decoded_response = response.json()
            print(f'"{decoded_response.get("name")}" attribute is created')

    print('Attributes loading finished!\n')


def send_attribute_values(attribute_values: list[dict]):
    print('Loading attribute values to the server...')
    characteristic_values_url = config.mb_characteristic_values_url

    for value in attribute_values:
        response = requests.post(characteristic_values_url, json=value)

        if response.status_code == 201:
            decoded_response = response.json()
            print(f'"{decoded_response.get("value")}" attribute value is created')
        elif response.status_code != 200:
            print(f'There was a problem loading "{value.get("value")}" attribute value')

    print('Attributes loading finished!\n')


