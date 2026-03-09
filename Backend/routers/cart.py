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

    # Get or create the cart for this user
    cart = db.query(Cart).filter(Cart.user_id == payload.user_id).first()
    if not cart:
        cart = Cart(user_id=payload.user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    for i in payload.items:
        fish = db.query(Fish).filter(Fish.id == i.fish_id).first()
        if not fish:
            raise HTTPException(status_code=404, detail=f"Fish {i.fish_id} not found")

        # BUG FIX #3: Previously always created a new CartItem row, so adding
        # the same fish twice created duplicate rows and broke the cart total.
        # Now we check if a CartItem for this fish already exists in the cart
        # and update its quantity instead of inserting a duplicate.
        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.fish_id == i.fish_id
        ).first()

        if existing_item:
            existing_item.quantity += i.quantity
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
    """Clear all items from a user's cart (called after order is placed)."""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    db.refresh(cart)
    return cart