import os

from dotenv import (
    load_dotenv,
)


load_dotenv()


# Markets-Bridge
mb_domain = os.getenv('MB_DOMAIN')

if not mb_domain:
    raise ValueError('MB_DOMAIN not set')

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
    raise ValueError('TRENDYOL_ID not set')

mb_login = os.getenv('MB_LOGIN')
mb_password = os.getenv('MB_PASSWORD')

if not (mb_login and mb_password):
    raise ValueError('MB_LOGIN and MB_PASSWORD not set for Markets-Bridge authentication')

mb_token_url = mb_domain + 'api/token/'
mb_token_refresh_url = mb_token_url + 'refresh/'
mb_system_environments_url = mb_domain + 'api/v1/common/system_environments/'
mb_logs_url = mb_domain + 'api/v1/common/logs/'


# Trendyol
trendyol_domain = 'https://www.trendyol.com'
trendyol_images_domain = 'https://cdn.dsmcdn.com'
trendyol_product_group_url = 'https://public.trendyol.com/discovery-web-websfxproductgroups-santral/api/v1/product-groups/'

