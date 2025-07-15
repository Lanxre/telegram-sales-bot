from typing import List, Optional

from pydantic import BaseModel
from core.internal.models import ProductItem

from dataclasses import dataclass


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


@dataclass
class CartCallbackData:
    action: str
    current_index: int
    product_id: int

    @classmethod
    def parse(cls, data: str) -> Optional["CartCallbackData"]:
        try:
            parts = data.split("_")
            return cls(
                action=parts[1], current_index=int(parts[3]), product_id=int(parts[4])
            )
        except (IndexError, ValueError):
            return None
