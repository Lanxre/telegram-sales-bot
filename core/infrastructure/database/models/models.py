from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    LargeBinary,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime


from .base import BaseModel


class Product(BaseModel):
    __tablename__ = "Product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    image = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to orders through Product_Order
    orders = relationship("Order", secondary="Product_Order", back_populates="products")


class ProductOrder(BaseModel):
    __tablename__ = "Product_Order"

    product_id = Column(Integer, ForeignKey("Product.id"), primary_key=True)
    order_id = Column(Integer, ForeignKey("Order.id"), primary_key=True)

    # Relationships
    product = relationship("Product", backref="product_orders")
    order = relationship("Order", backref="order_products")


class Order(BaseModel):
    __tablename__ = "Order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_price = Column(Float, nullable=False)
    total_count = Column(Integer, nullable=False)
    order_note = Column(Text)
    user_id = Column(Integer, ForeignKey("users.telegram_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="orders")
    products = relationship(
        "Product", secondary="Product_Order", back_populates="orders"
    )


class User(BaseModel):
    __tablename__ = "users"

    telegram_id = Column(Integer, primary_key=True)
    username = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to orders
    orders = relationship("Order", back_populates="user")
