import json
import re

import requests

import config


def parse_product(url: str):
    response = requests.get(url)
    pattern = r'__PRODUCT_DETAIL_APP_INITIAL_STATE__\s*=\s*(?P<json_data>.*?);\s*window'
    match = re.search(pattern, response.text)

    if match:
        raw_json = match.group('json_data')
        json_object = json.loads(raw_json)
        product = json_object.get('product')

        print(f'Товар {product.get("name")} найден.')
        attributes, attribute_values = unpack_attributes(
            product.get('attributes'),
            product.get('originalCategory', {}).get('id'),
        )
        send_attributes(attributes)
        send_attribute_values(attribute_values)
        send_product(product)
    else:
        print(f'Не найдено соответствие для url {url}.')


def unpack_attributes(attributes: list[dict], category_id: int) -> tuple[list[dict], list[dict]]:
    processed_attributes = []
    processed_attribute_values = []

    for attribute_data in attributes:
        attribute = attribute_data.get('key', {})
        processed_attributes.append(
            dict(
                external_id=attribute.get('id'),
                name=attribute.get('name'),
                category_external_ids=[category_id],
                marketplace_id=config.marketplace_id,
            )
        )
        attribute_value = attribute_data.get('value', {})
        processed_attribute_values.append(
            dict(
                external_id=attribute_value.get('id'),
                value=attribute_value.get('name'),
                characteristic_external_id=attribute.get('id'),
                marketplace_id=config.marketplace_id,
            )
        )

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