from dataclasses import (
    dataclass,
    field,
)
from decimal import (
    Decimal,
)


@dataclass
class MBCategoryDTO:
    external_id: int
    name: str
    marketplace_id: int


@dataclass
class MBCharacteristicDTO:
    external_id: int
    name: str
    category_external_ids: list[int]
    marketplace_id: int


@dataclass
class MBCharacteristicValueDTO:
    external_id: int
    value: str
    characteristic_external_id: int
    marketplace_id: int


@dataclass
class MBBrandDTO:
    external_id: int
    name: str
    marketplace_id: int


@dataclass
class MBImageDTO:
    image_url: str
    product_id: int


@dataclass
class MBProductDTO:
    external_id: int
    name: str
    url: str
    price: int | float | Decimal
    discounted_price: int | float | Decimal
    stock_quantity: int
    product_code: str
    category_external_id: int
    brand_external_id: int
    characteristic_value_external_ids: list[int]
    marketplace_id: int
