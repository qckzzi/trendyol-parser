#!/usr/bin/env python
import json
import logging

import pika

from markets_bridge.utils import (
    Formatter,
    Sender,
    write_log_entry,
)
from trendyol.utils import (
    Parser,
)


def callback(ch, method, properties, body):
    message = json.loads(body)

    try:
        processing_type = message['type']
        processing_url = message['url']

        logging.info(f'{processing_type.lower().capitalize()} was received for parsing. URL: {processing_url}')

        processing_map = {
            'PRODUCT': product_card_processing,
            'CATEGORY': category_processing,
        }

        processing_function = processing_map[processing_type]
        processing_function(processing_url)
    except KeyError as e:
        error = f'Body validation error: {e}'
        write_log_entry(error)
        logging.error(error)
        return
    except Exception as e:
        error = f'There was a problem: {e}'
        write_log_entry(error)
        logging.exception(error)
        return


def category_processing(url: str):
    product_url_list = Parser.parse_product_urls_by_category_url(url)

    for product_url in product_url_list:
        product_processing(product_url)


def product_card_processing(url: str):
    trendyol_product_urls = Parser.parse_product_urls_by_product_card_url(url)

    if not trendyol_product_urls:
        product_processing(url)

    for product_url in trendyol_product_urls:
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
            Sender.get_and_send_image(image_url, product['id'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    connection_parameters = pika.ConnectionParameters(host='localhost', heartbeat=300, blocked_connection_timeout=300)
    with pika.BlockingConnection(connection_parameters) as connection:
        channel = connection.channel()
        channel.queue_declare('parsing')
        channel.basic_consume('parsing', callback, auto_ack=True)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            pass
