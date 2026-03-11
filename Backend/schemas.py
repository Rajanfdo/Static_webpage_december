from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ──────────────────────────────────────────
# LOGIN
# ──────────────────────────────────────────

class LoginCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: Optional[str] = None
    # BUG FIX #2: was required `datetime` — model has a server-side default,
    # so the client should never need to send this field.
    created_at: Optional[datetime] = None


class LoginOut(BaseModel):
    login_id: int
    username: str
    email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# ADDRESS
# ──────────────────────────────────────────

class AddressCreate(BaseModel):
    login_id: int
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None


class AddressOut(AddressCreate):
    address_id: int

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# USERS
# ──────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: str
    password: Optional[str] = None
    role: Optional[str] = "customer"
    phone: Optional[str] = None
    address: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


# BUG FIX #6: New schema for the POST /api/users/login endpoint so the
# frontend can authenticate without fetching the entire users list.
class UserLogin(BaseModel):
    email: str
    password: str


# ──────────────────────────────────────────
# CATEGORY
# ──────────────────────────────────────────

class CategoryCreate(BaseModel):
    category_name: str
    description: Optional[str] = None


class CategoryOut(CategoryCreate):
    category_id: int

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# FISH
# ──────────────────────────────────────────

class FishCreate(BaseModel):
    name: str
    description: Optional[str] = None
    stock: int
    category_id: Optional[int] = None
    price: Optional[int] = None
    img_url: Optional[str] = None


class FishOut(FishCreate):
    id: int

    # BUG FIX #1: model_config dict was placed OUTSIDE the class body so
    # orm_mode never activated. All fish endpoints were returning Pydantic
    # validation errors. Fixed by using the proper inner Config class.
    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# ORDER ITEMS & ORDERS
# ──────────────────────────────────────────

class OrderItemCreate(BaseModel):
    fish_id: int
    quantity: int


class OrderCreate(BaseModel):
    user_id: int
    delivery_address: str
    items: List[OrderItemCreate]


class OrderItemOut(BaseModel):
    id: int
    order_id: int
    fish_id: int
    quantity: int

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    user_id: int
    delivery_address: str
    created_at: datetime
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# REVIEWS
# ──────────────────────────────────────────

class ReviewCreate(BaseModel):
    user_id: int
    fish_id: int
    rating: int


class ReviewOut(ReviewCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# ADMIN
# ──────────────────────────────────────────

class AdminCreate(BaseModel):
    username: str
    email: str
    password: str


class AdminOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# BUG FIX #5: New schema so admin login uses a JSON request body
# instead of exposing credentials as query parameters in the URL.
class AdminLogin(BaseModel):
    email: str
    password: str


# ──────────────────────────────────────────
# CART
# ──────────────────────────────────────────

class CartItemCreate(BaseModel):
    fish_id: int
    quantity: int = 1


class CartItemOut(BaseModel):
    id: int
    fish_id: int
    quantity: int

    class Config:
        from_attributes = True


class CartCreate(BaseModel):
    user_id: int
    items: List[CartItemCreate]


class CartOut(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    items: List[CartItemOut] = []

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# CONTACT US
# ──────────────────────────────────────────

class ContactUsCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


class ContactUsOut(BaseModel):
    id: int
    name: str
    email: str
    subject: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True