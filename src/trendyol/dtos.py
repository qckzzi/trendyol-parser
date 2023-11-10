from dataclasses import (
    dataclass,
    field,
)
from decimal import (
    Decimal,
)


@dataclass
class TrendyolCategoryDTO:
    id: int
    name: str


@dataclass
class TrendyolAttributeDTO:
    id: int
    name: str


@dataclass
class TrendyolAttributeValueDTO:
    id: int
    value: str
    attribute: TrendyolAttributeDTO


@dataclass
class TrendyolBrandDTO:
    id: int
    name: str
    path: str


@dataclass
class TrendyolProductDTO:
    id: int
    name: str
    product_group_id: int
    url: str
    product_code: str
    category: TrendyolCategoryDTO
    brand: TrendyolBrandDTO
    item_number: int
    stock_quantity: int
    price: int | float | Decimal
    discounted_price: int | float | Decimal
    image_urls: list[str] = field(default_factory=list)
    values: list[TrendyolAttributeValueDTO] = field(default_factory=list)
