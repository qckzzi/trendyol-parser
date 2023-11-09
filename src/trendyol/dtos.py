from dataclasses import (
    dataclass,
    field,
)
from decimal import (
    Decimal,
)


@dataclass
class CategoryDTO:
    id: int
    name: str


@dataclass
class AttributeDTO:
    id: int
    name: str


@dataclass
class AttributeValueDTO:
    id: int
    value: str
    attribute: AttributeDTO


@dataclass
class ProductVariantDTO:
    item_number: int
    stock_quantity: int
    price: float | Decimal
    value: str


@dataclass
class BrandDTO:
    id: int
    name: str
    path: str


@dataclass
class ProductDTO:
    id: int
    name: str
    product_group_id: int
    url: str
    product_code: str
    category: CategoryDTO
    brand: BrandDTO
    variants: list[ProductVariantDTO] = field(default_factory=list)
    values: list[AttributeValueDTO] = field(default_factory=list)
