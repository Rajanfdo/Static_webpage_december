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

    # Build a set of fish_ids sent in this request
    incoming_fish_ids = {i.fish_id for i in payload.items}

    # Remove items that are NOT in the incoming list (supports "remove item" from frontend)
    db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.fish_id.notin_(incoming_fish_ids)
    ).delete(synchronize_session=False)

    for i in payload.items:
        fish = db.query(Fish).filter(Fish.id == i.fish_id).first()
        if not fish:
            raise HTTPException(status_code=404, detail=f"Fish {i.fish_id} not found")

        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.fish_id == i.fish_id
        ).first()

        if existing_item:
            # FIX: SET the quantity (=), don't ADD to it (+=)
            # The frontend sends the full desired quantity, not a delta.
            existing_item.quantity = i.quantity
        else:
            new_item = CartItem(cart_id=cart.id, fish_id=i.fish_id, quantity=i.quantity)
            db.add(new_item)

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
    """Clear all items from a user's cart."""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    db.refresh(cart)
    return cart


@router.delete("/{user_id}/item/{fish_id}")
def remove_cart_item(user_id: int, fish_id: int, db: Session = Depends(get_db)):
    """Remove a single item from the cart."""
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