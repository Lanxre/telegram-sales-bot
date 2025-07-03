from typing import List

from pydantic import BaseModel


class ShopCardContent(BaseModel):
    id: int
    product_id: int
    name: str
    price: float
    quantity: int
    total: float


class ShopCardTotal(BaseModel):
    items_count: int
    total_price: int
    items: List[ShopCardContent]
