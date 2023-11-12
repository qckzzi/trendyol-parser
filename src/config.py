import os

from dotenv import (
    load_dotenv,
)


load_dotenv()


# Markets-Bridge
mb_domain = os.getenv('MB_DOMAIN')

if not mb_domain:
    raise ValueError('Не задан домен Markets-Bridge.')

mb_categories_url = mb_domain + 'api/v1/provider/categories/'
mb_products_url = mb_domain + 'api/v1/provider/products/'
mb_characteristics_url = mb_domain + 'api/v1/provider/characteristics/'
mb_characteristic_values_url = mb_domain + 'api/v1/provider/characteristic_values/'
mb_product_images_url = mb_domain + 'api/v1/provider/product_images/'
mb_brands_url = mb_domain + 'api/v1/provider/brands/'

mb_target_products_url = mb_domain + 'api/v1/parser_targets/products/'
mb_target_categories_url = mb_domain + 'api/v1/parser_targets/categories/'

marketplace_id = int(os.getenv('TRENDYOL_ID', default=0))

if not marketplace_id:
    raise ValueError('Не задан ID записи маркетплейса "Trendyol", находящейся в БД Markets-Bridge.')


# Trendyol
trendyol_domain = 'https://www.trendyol.com'
trendyol_images_domain = 'https://cdn.dsmcdn.com'
trendyol_product_group_url = 'https://public.trendyol.com/discovery-web-websfxproductgroups-santral/api/v1/product-groups/'

