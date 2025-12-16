from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date



class LoginCreate(BaseModel):
    username: str
    email: Optional[str]
    password: Optional[str]
    created_at: datetime 

class LoginOut(BaseModel):
    login_id: int
    username: str
    email: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True



class AddressCreate(BaseModel):
    login_id: int
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    country: Optional[str]


class AddressOut(AddressCreate):
    address_id: int

    class Config:
        orm_mode = True



class UserCreate(BaseModel):
    name: str
    email: str
    password: Optional[str]
    role: Optional[str] = "customer"
    phone: Optional[str]
    address: Optional[str]


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: Optional[str]
    phone: Optional[str]

    class Config:
        orm_mode = True


# ---- Category ----
class CategoryCreate(BaseModel):
    category_name: str
    description: Optional[str]


class CategoryOut(CategoryCreate):
    category_id: int

    class Config:
        orm_mode = True



class FishCreate(BaseModel):
    name: str
    description: Optional[str]
    stock: int
    catch_date: Optional[date]
    category_id: Optional[int]


class FishOut(FishCreate):
    id: int

    class Config:
        orm_mode = True



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
        orm_mode = True


class OrderOut(BaseModel):
    id: int
    user_id: int
    delivery_address: str
    created_at: datetime
    items: List[OrderItemOut] = []

    class Config:
        orm_mode = True


class OrderTrackingCreate(BaseModel):
    order_id: int
    login_id: int
    category_id: int
    address_id: int
    status: str


class OrderTrackingOut(OrderTrackingCreate):
    order_date: datetime

    class Config:
        orm_mode = True


class ReviewCreate(BaseModel):
    user_id: int
    fish_id: int
    rating: int


class ReviewOut(ReviewCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
