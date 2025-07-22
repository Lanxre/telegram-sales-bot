from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from core.internal.enums import OrderStatus


class Product(BaseModel):
    __tablename__ = "Product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    image_file_id: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Primary many-to-many relationship to orders
    orders: Mapped[List["Order"]] = relationship(
        secondary="Product_Order",
        back_populates="products",
    )
    # Auxiliary relationship to ProductOrder (read-only)
    product_orders: Mapped[List["ProductOrder"]] = relationship(
        back_populates="product",
        viewonly=True,  # Make read-only to avoid foreign key conflicts
    )
    shop_card_items: Mapped[List["ShopCardItem"]] = relationship(
        back_populates="product"
    )


class ProductOrder(BaseModel):
    __tablename__ = "Product_Order"

    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Product.id"), primary_key=True
    )
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Order.id"), primary_key=True
    )
    product_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship(
        back_populates="product_orders",
        viewonly=True,  # Make read-only to avoid foreign key conflicts
    )
    order: Mapped["Order"] = relationship(
        back_populates="order_products",
        viewonly=True,  # Make read-only to avoid foreign key conflicts
    )


class Order(BaseModel):
    __tablename__ = "Order"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False)
    order_note: Mapped[Optional[str]] = mapped_column(Text)
    delivery_address: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.telegram_id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Many-to-one relationship to user
    user: Mapped["User"] = relationship(back_populates="orders")
    # Primary many-to-many relationship to products
    products: Mapped[List["Product"]] = relationship(
        secondary="Product_Order",
        back_populates="orders",
    )
    # Auxiliary relationship to ProductOrder (read-only)
    order_products: Mapped[List["ProductOrder"]] = relationship(
        back_populates="order",
        viewonly=True,  # Make read-only to avoid foreign key conflicts
    )


class Dialog(BaseModel):
    __tablename__ = "dialogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user1_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.telegram_id"), nullable=False
    )
    user2_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.telegram_id"), nullable=False
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    user1: Mapped["User"] = relationship(
        foreign_keys=[user1_id], back_populates="dialogs_as_user1"
    )
    user2: Mapped["User"] = relationship(
        foreign_keys=[user2_id], back_populates="dialogs_as_user2"
    )
    messages: Mapped[List["Message"]] = relationship(back_populates="dialog")

    def __repr__(self):
        return f"<Dialog(id={self.id}, user1_id={self.user1_id}, user2_id={self.user2_id})>"


class Message(BaseModel):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dialog_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dialogs.id"), nullable=False
    )
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.telegram_id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )

    # Relationships
    dialog: Mapped["Dialog"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship(back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, dialog_id={self.dialog_id}, sender_id={self.sender_id}, content='{self.content[:20]}...')>"


class ShopCard(BaseModel):
    __tablename__ = "shop_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.telegram_id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="shop_cards")
    items: Mapped[List["ShopCardItem"]] = relationship(
        back_populates="shop_card", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ShopCard(id={self.id}, user_id={self.user_id})>"


class ShopCardItem(BaseModel):
    __tablename__ = "shop_card_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_card_id: Mapped[int] = mapped_column(ForeignKey("shop_cards.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("Product.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )

    shop_card: Mapped["ShopCard"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()

    def __repr__(self):
        return f"<ShopCardItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"


class User(BaseModel):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String)
    full_name: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # One-to-many relationship to orders
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    dialogs_as_user1: Mapped[List["Dialog"]] = relationship(
        foreign_keys="Dialog.user1_id", back_populates="user1"
    )
    dialogs_as_user2: Mapped[List["Dialog"]] = relationship(
        foreign_keys="Dialog.user2_id", back_populates="user2"
    )
    shop_cards: Mapped[List["ShopCard"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    messages: Mapped[List["Message"]] = relationship(back_populates="sender")

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, full_name={self.full_name})>"
