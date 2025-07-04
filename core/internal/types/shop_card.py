from typing import List, Optional

from pydantic import BaseModel
from core.internal.models import ProductItem


class ShopCardContent(BaseModel):
    id: int
    product_id: int
    name: str
    price: float
    quantity: int
    total: float
    product: Optional[ProductItem] = None


class ShopCardTotal(BaseModel):
    items_count: int
    total_price: float
    items: List[ShopCardContent]
