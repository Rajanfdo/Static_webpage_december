from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Orders, OrderItem, Users, Fish
from schemas import OrderCreate, OrderOut, OrderItemCreate, OrderItemOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=OrderOut)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    order = Orders(user_id=payload.user_id, delivery_address=payload.delivery_address)
    db.add(order)
    db.commit()
    db.refresh(order)

    items_out = []
    for it in payload.items:
        fish = db.query(Fish).filter(Fish.id == it.fish_id).first()
        if not fish:
            db.delete(order)
            db.commit()
            raise HTTPException(status_code=404, detail=f"Fish {it.fish_id} not found")
        oi = OrderItem(order_id=order.id, fish_id=it.fish_id, quantity=it.quantity)
        db.add(oi)
        # optionally decrease stock
        if fish.stock is not None:
            fish.stock = max(0, fish.stock - it.quantity)
        db.commit()
        db.refresh(oi)
        items_out.append(oi)

    order.items = items_out
    db.refresh(order)
    return order


@router.get("/", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Orders).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Orders).filter(Orders.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    return o
