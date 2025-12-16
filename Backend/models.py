from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Login(Base):
    __tablename__ = "login"
    login_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(150))
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    addresses = relationship("Address", back_populates="login")
    order_tracking = relationship("OrderTracking", back_populates="login")


class Address(Base):
    __tablename__ = "address"
    address_id = Column(Integer, primary_key=True, index=True)
    login_id = Column(Integer, ForeignKey("login.login_id"))
    street = Column(String(150))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    country = Column(String(100))

    login = relationship("Login", back_populates="addresses")
    order_tracking = relationship("OrderTracking", back_populates="address")


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))
    email = Column(String(200))
    password = Column(String(255))
    role = Column(String(50))
    phone = Column(String(20))
    address = Column(Text)

    orders = relationship("Orders", back_populates="user")
    reviews = relationship("Review", back_populates="user")


class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100))
    description = Column(Text)

    fishes = relationship("Fish", back_populates="category")
    order_tracking = relationship("OrderTracking", back_populates="category")


class Fish(Base):
    __tablename__ = "fishes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    description = Column(Text)
    stock = Column(Integer)
    catch_date = Column(Date)
    category_id = Column(Integer, ForeignKey("categories.category_id"))

    category = relationship("Category", back_populates="fishes")
    order_items = relationship("OrderItem", back_populates="fish")
    reviews = relationship("Review", back_populates="fish")


class Orders(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    delivery_address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("Users", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_item"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    fish_id = Column(Integer, ForeignKey("fishes.id"))
    quantity = Column(Integer)

    order = relationship("Orders", back_populates="items")
    fish = relationship("Fish", back_populates="order_items")


class OrderTracking(Base):
    __tablename__ = "order_tracking"
    order_id = Column(Integer, primary_key=True, index=True)
    login_id = Column(Integer, ForeignKey("login.login_id"))
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    address_id = Column(Integer, ForeignKey("address.address_id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50))

    login = relationship("Login", back_populates="order_tracking")
    category = relationship("Category", back_populates="order_tracking")
    address = relationship("Address", back_populates="order_tracking")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    fish_id = Column(Integer, ForeignKey("fishes.id"))
    rating = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("Users", back_populates="reviews")
    fish = relationship("Fish", back_populates="reviews")


