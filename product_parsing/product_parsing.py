import requests
import re
import json

from core import config


def parse_product(url: str, headers: dict):
    response = requests.get(url, headers=headers)
    pattern = r'__PRODUCT_DETAIL_APP_INITIAL_STATE__=(?P<json_data>.*?);window'
    match = re.search(pattern, response.text)

    if match:
        raw_json = match.group('json_data')
        json_object = json.loads(raw_json)
        product = json_object.get('product')

        print(f'Товар {product.get('name')} найден.')
        send_product(product)
    else:
        print(f'Не найдено соответствие для url {url}.')

    print('\n')


def send_product(product):
    data = dict(
        name=product.get('name'),
        price=product.get('price', {}).get('originalPrice', {}),
        external_id=product.get('id'),
        provider_category_external_id=product.get('originalCategory', {}).get('id'),
    )
    response = requests.post(
        config.get('markets_bridge', 'scrapped_products_url'),
        json=data,
    )
    if response.status_code == 201:
        print(f'Товар {product.get('name')} успешно создан')
        product_id = response.json().get('id')
        for image_path in product.get('images'):
            marketplace_url = config.get('trendyol', 'content_domain')
            image_url = f'{marketplace_url}{image_path}'
            parse_image(image_url, product_id)

    else:
        print(f'Ошибка создания товара {product.get('name')}\nSTATUS: {response.status_code}\n')


def parse_image(url, product_id):
    get_image_response = requests.get(url)
    data = dict(
        image=get_image_response.content,
        product=product_id,
    )
    response = requests.post(
        config.get('markets_bridge', 'product_images_url'),
        files=data,
    )
    if response.status_code == 201:
        print(f'Изображение успешно создано.')
    else:
        print(f'Ошибка создания изображения\nSTATUS: {response.status_code}')
