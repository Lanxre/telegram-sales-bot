from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.internal.enums import OrderStatus


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


class ProductItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    price: float
    image: Optional[bytes] = None


class OrderCreate(BaseModel):
    user_id: int
    total_price: float
    total_count: int
    order_note: Optional[str] = None
    delivery_address: Optional[str] = None
    products: Optional[List[ProductItem]] = None
    status: Optional[OrderStatus] = None


class OrderUpdate(BaseModel):
    total_price: Optional[float] = None
    total_count: Optional[int] = None
    order_note: Optional[str] = None
    delivery_address: Optional[str] = None
    status: Optional[OrderStatus] = None
    products: List[ProductUpdate] = Field(..., min_length=1)


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


class DialogCreate(BaseModel):
    id: int
    user1_id: int
    user2_id: int


class DialogUpdate(BaseModel):
    user1_id: Optional[int] = None
    user2_id: Optional[int] = None
    is_read: Optional[bool] = None


class MessageCreate(BaseModel):
    id: int
    dialog_id: int
    sender_id: int
    content: str


class MessageUpdate(BaseModel):
    content: str


class ShopCardItemCreate(BaseModel):
    shop_card_id: Optional[int] = None
    product_id: int = Field(..., gt=0)
    quantity: int = Field(1, gt=0, le=100)


class ShopCardCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    items: Optional[List[ShopCardItemCreate]] = None


class ShopCardItemUpdate(BaseModel):
    id: Optional[int] = Field(None, gt=0)
    product_id: Optional[int] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, gt=0, le=100)


class ShopCardUpdate(BaseModel):
    items: List[ShopCardItemUpdate] = Field(..., min_length=1)
