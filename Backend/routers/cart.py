from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Cart, CartItem, Users, Fish
from schemas import CartCreate, CartOut, CartItemCreate
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_cart(user_id: int, db: Session) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


# ── POST /api/cart/ — ADDS items, never deletes existing ones ─────────────────
# Used by menu, offers pages when clicking "Add to Cart"
@router.post("/", response_model=CartOut)
def add_to_cart(payload: CartCreate, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart = get_or_create_cart(payload.user_id, db)

    for i in payload.items:
        fish = db.query(Fish).filter(Fish.id == i.fish_id).first()
        if not fish:
            raise HTTPException(status_code=404, detail=f"Fish {i.fish_id} not found")

        existing = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.fish_id == i.fish_id
        ).first()

        if existing:
            existing.quantity += i.quantity          # ADD to existing quantity
        else:
            db.add(CartItem(
                cart_id=cart.id,
                fish_id=i.fish_id,
                quantity=i.quantity
            ))

    db.commit()
    db.refresh(cart)
    return cart


# ── POST /api/cart/sync — REPLACES full cart ──────────────────────────────────
# Used only by the cart page when user changes quantities
class SyncItem(BaseModel):
    fish_id: int
    quantity: int
    unit_price: Optional[float] = None

class SyncPayload(BaseModel):
    user_id: int
    items: List[SyncItem]

@router.post("/sync", response_model=CartOut)
def sync_cart(payload: SyncPayload, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart = get_or_create_cart(payload.user_id, db)

    incoming_fish_ids = {i.fish_id for i in payload.items}

    # Remove items not in the incoming list
    db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.fish_id.notin_(incoming_fish_ids)
    ).delete(synchronize_session=False)

    for i in payload.items:
        fish = db.query(Fish).filter(Fish.id == i.fish_id).first()
        if not fish:
            raise HTTPException(status_code=404, detail=f"Fish {i.fish_id} not found")

        existing = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.fish_id == i.fish_id
        ).first()

        if existing:
            existing.quantity = i.quantity           # SET quantity exactly
        else:
            db.add(CartItem(
                cart_id=cart.id,
                fish_id=i.fish_id,
                quantity=i.quantity
            ))

    db.commit()
    db.refresh(cart)
    return cart


@router.get("/{user_id}", response_model=CartOut)
def view_cart(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@router.delete("/{user_id}", response_model=CartOut)
def clear_cart(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    db.refresh(cart)
    return cart


@router.delete("/{user_id}/item/{fish_id}")
def remove_cart_item(user_id: int, fish_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.fish_id == fish_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    db.delete(item)
    db.commit()
    return {"message": "Item removed"}