from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    image_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price"),
        CheckConstraint("stock >= 0", name="ck_products_stock"),
    )


class AppUser(Base):
    __tablename__ = "app_users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())


class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_users.user_id"), nullable=False, unique=True)


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.cart_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_cart_items_quantity"),
        UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
    )


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_users.user_id"), nullable=False)
    status = Column(String(30), nullable=False, default="PENDING")
    total_amount = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
