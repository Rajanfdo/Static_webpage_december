from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Cart, CartItem, Users, Fish
from schemas import CartCreate, CartOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/", response_model=CartOut)
def add_to_cart(payload: CartCreate, db: Session = Depends(get_db)):

    user = db.query(Users).filter(Users.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart = db.query(Cart).filter(Cart.user_id == payload.user_id).first()
    if not cart:
        cart = Cart(user_id=payload.user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    for i in payload.items:
        fish = db.query(Fish).filter(Fish.id == i.fish_id).first()
        if not fish:
            raise HTTPException(status_code=404, detail="Fish not found")

        item = CartItem(cart_id=cart.id, fish_id=i.fish_id, quantity=i.quantity)
        db.add(item)

    db.commit()
    db.refresh(cart)
    return cart



@router.get("/{user_id}", response_model=CartOut)
def view_cart(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart
