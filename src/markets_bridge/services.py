import logging
import uuid
from dataclasses import (
    asdict,
)

import requests
from requests import (
    Response,
)

import config
from markets_bridge.dtos import (
    MBBrandDTO,
    MBCategoryDTO,
    MBCharacteristicDTO,
    MBCharacteristicValueDTO,
    MBProductDTO,
)
from trendyol.dtos import (
    TrendyolProductDTO,
)


class Formatter:
    """Data formatter for Markets-Bridge service."""

    product_data_class = MBProductDTO
    category_data_class = MBCategoryDTO
    characteristic_data_class = MBCharacteristicDTO
    characteristic_value_data_class = MBCharacteristicValueDTO
    brand_data_class = MBBrandDTO

    def __init__(self):
        self._trendyol_product = None

    @property
    def trendyol_product(self) -> TrendyolProductDTO:
        return self._trendyol_product

    @trendyol_product.setter
    def trendyol_product(self, trendyol_product: TrendyolProductDTO):
        if not isinstance(trendyol_product, TrendyolProductDTO):
            raise ValueError('Trendyol product must be TrendyolProductDTO')

        self._trendyol_product = trendyol_product

    def get_product(self) -> product_data_class:
        product = self.product_data_class(
            external_id=self.trendyol_product.id,
            name=self.trendyol_product.name,
            url=self.trendyol_product.url,
            price=self.trendyol_product.price,
            discounted_price=self.trendyol_product.discounted_price,
            stock_quantity=self.trendyol_product.stock_quantity,
            product_code=self.trendyol_product.product_code,
            category_external_id=self.trendyol_product.category.id,
            brand_external_id=self.trendyol_product.brand.id,
            characteristic_value_external_ids=[value.id for value in self.trendyol_product.values],
            marketplace_id=config.marketplace_id,
        )

        return product

    def get_category(self) -> category_data_class:
        category = self.category_data_class(
            external_id=self.trendyol_product.category.id,
            name=self.trendyol_product.category.name,
            marketplace_id=config.marketplace_id,
        )

        return category

    def get_brand(self) -> brand_data_class:
        brand = self.brand_data_class(
            external_id=self.trendyol_product.brand.id,
            name=self.trendyol_product.brand.name,
            marketplace_id=config.marketplace_id,
        )

        return brand

    def get_characteristics(self) -> list[characteristic_data_class]:
        characteristic_list = []

        for value in self.trendyol_product.values:

            characteristic = self.characteristic_data_class(
                external_id=value.attribute.id,
                name=value.attribute.name,
                category_external_ids=[self.trendyol_product.category.id],
                marketplace_id=config.marketplace_id,
            )

            characteristic_list.append(characteristic)

        return characteristic_list

    def get_characteristic_values(self) -> list[characteristic_value_data_class]:
        values = []

        for trendyol_value in self.trendyol_product.values:
            mb_value = self.characteristic_value_data_class(
                external_id=trendyol_value.id,
                value=trendyol_value.value,
                characteristic_external_id=trendyol_value.attribute.id,
                marketplace_id=config.marketplace_id,
            )

            values.append(mb_value)

        return values


class Sender:
    """Data sender to Markets-Bridge service."""

    @classmethod
    def send_product(cls, product: MBProductDTO):
        logging.info(f'Sending "{product.name}" product.')

        return cls._send_object(
            product,
            url=config.mb_products_url,
        )

    @classmethod
    def send_category(cls, category: MBCategoryDTO):
        logging.info(f'Sending "{category.name}" category.')

        return cls._send_object(
            category,
            url=config.mb_categories_url,
        )

    @classmethod
    def send_characteristic(cls, characteristic: MBCharacteristicDTO):
        logging.info(f'Sending "{characteristic.name}" characteristic.')

        return cls._send_object(
            characteristic,
            url=config.mb_characteristics_url,
        )

    @classmethod
    def send_characteristic_value(cls, value: MBCharacteristicValueDTO):
        logging.info(f'Sending "{value.value}" value.')

        return cls._send_object(
            value,
            url=config.mb_characteristic_values_url,
        )

    @classmethod
    def send_brand(cls, brand: MBBrandDTO):
        logging.info(f'Sending "{brand.name}" brand.')

        return cls._send_object(
            brand,
            url=config.mb_brands_url,
        )

    @classmethod
    def send_image(cls, image_url: str, product_id: int):
        logging.info(f'Receipt and sending image by url: {image_url}.')

        try:
            image_response = requests.get(image_url)
        except (requests.HTTPError, requests.ConnectionError, requests.ConnectTimeout):
            logging.error('An error occurred while receiving the image. Try again...')
            cls.send_image(image_url, product_id)

            return
        else:
            image = image_response.content

        response = requests.post(
            config.mb_product_images_url,
            data={'product': product_id},
            files={'image': (f'{uuid.uuid4().hex}.jpg', image)},
        )
        response.raise_for_status()

        return response.json()

    @staticmethod
    def _send_object(obj, url) -> Response:
        response = requests.post(url, json=asdict(obj))
        response.raise_for_status()

        return response
