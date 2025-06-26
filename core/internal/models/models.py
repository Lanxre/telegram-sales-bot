from typing import List, Optional
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image: Optional[bytes] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[bytes] = None

class OrderCreate(BaseModel):
    total_price: float
    total_count: int
    order_note: Optional[str] = None
    user_id: int
    product_ids: Optional[List[int]] = None

class OrderUpdate(BaseModel):
    total_price: Optional[float] = None
    total_count: Optional[int] = None
    order_note: Optional[str] = None
    product_ids: Optional[List[int]] = None

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None

class ProductOrderCreate(BaseModel):
    product_id: int
    order_id: int