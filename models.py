from sqlalchemy import (Column, Integer, String, Float, ForeignKey, Boolean, DateTime)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="buyer")

    products = relationship("Product", back_populates="seller")
    cart = relationship(
    "Cart",
    back_populates="user",
    uselist=False,
    cascade="all, delete-orphan"
)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    description = Column(String, nullable=True)

    price = Column(Float, nullable=False)

    stock = Column(Integer, default=0)

    seller_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    seller = relationship(
        "User",
        back_populates="products"
    )
    
class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="cart"
    )

    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)

    cart_id = Column(
        Integer,
        ForeignKey("carts.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        default=1
    )

    cart = relationship(
        "Cart",
        back_populates="items"
    )

    product = relationship("Product")
    
class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(
        String,
        unique=True,
        nullable=False
    )

    discount_percent = Column(
        Float,
        nullable=False
    )

    minimum_amount = Column(
        Float,
        default=0
    )

    expiry_date = Column(
        DateTime,
        nullable=False
    )

    active = Column(
        Boolean,
        default=True
    )
    
class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    total_amount = Column(
        Float,
        nullable=False
    )

    discount_amount = Column(
        Float,
        default=0
    )

    final_amount = Column(
        Float,
        nullable=False
    )

    status = Column(
        String,
        default="pending"
    )

    user = relationship("User")

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    price = Column(
        Float,
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship("Product")
    
class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    status = Column(
        String,
        default="pending"
    )

    payment_method = Column(
        String,
        default="online"
    )

    transaction_id = Column(
        String,
        nullable=True
    )
    razorpay_order_id = Column(
    String,
    nullable=True
    )
    order = relationship("Order")