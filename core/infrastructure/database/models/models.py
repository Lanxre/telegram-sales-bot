from typing import List, Optional
from sqlalchemy import (
    Integer,
    String,
    Float,
    LargeBinary,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone


from .base import BaseModel


class Product(BaseModel):
    __tablename__ = "Product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

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

class ProductOrder(BaseModel):
    __tablename__ = "Product_Order"

    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("Product.id"), primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("Order.id"), primary_key=True)

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
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.telegram_id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

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

class User(BaseModel):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String)
    full_name: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # One-to-many relationship to orders
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
