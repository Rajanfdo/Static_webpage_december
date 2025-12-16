from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import OrderItem, Orders, Fish
from schemas import OrderItemOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[OrderItemOut])
def list_order_items(db: Session = Depends(get_db)):
    return db.query(OrderItem).all()


@router.get("/{item_id}", response_model=OrderItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    it = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not it:
        raise HTTPException(status_code=404, detail="Item not found")
    return it
