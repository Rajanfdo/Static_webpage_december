from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Backend.database import SessionLocal
from Backend.models import OrderTracking, Login, Category, Address
from Backend.schemas import OrderTrackingCreate, OrderTrackingOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=OrderTrackingOut)
def create_tracking(payload: OrderTrackingCreate, db: Session = Depends(get_db)):
    # Basic existence checks
    if not db.query(Login).filter(Login.login_id == payload.login_id).first():
        raise HTTPException(status_code=404, detail="Login not found")
    if not db.query(Category).filter(Category.category_id == payload.category_id).first():
        raise HTTPException(status_code=404, detail="Category not found")
    if not db.query(Address).filter(Address.address_id == payload.address_id).first():
        raise HTTPException(status_code=404, detail="Address not found")

    t = OrderTracking(
        order_id=payload.order_id,
        login_id=payload.login_id,
        category_id=payload.category_id,
        address_id=payload.address_id,
        status=payload.status
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.get("/", response_model=list[OrderTrackingOut])
def list_tracking(db: Session = Depends(get_db)):
    return db.query(OrderTracking).all()
