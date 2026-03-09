from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Orders, OrderItem, Users, Fish
from schemas import OrderCreate, OrderOut, OrderItemOut

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

    # BUG FIX #4 — Part A: Validate ALL fish IDs and stock BEFORE writing
    # anything to the database. The original code committed the Order row
    # first and then validated items in a loop. If any fish was invalid,
    # a ghost order record was left in the DB (the delete+commit attempt
    # was also unreliable because items already committed weren't rolled back).
    fish_objects = {}
    for it in payload.items:
        fish = db.query(Fish).filter(Fish.id == it.fish_id).first()
        if not fish:
            raise HTTPException(status_code=404, detail=f"Fish {it.fish_id} not found")
        if fish.stock is not None and fish.stock < it.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for '{fish.name}' (available: {fish.stock})"
            )
        fish_objects[it.fish_id] = fish

    # BUG FIX #4 — Part B: Only create the Order row after all validations pass.
    order = Orders(user_id=payload.user_id, delivery_address=payload.delivery_address)
    db.add(order)
    db.flush()  # assigns order.id without committing yet

    # Add all items and deduct stock in one go, then commit once atomically.
    for it in payload.items:
        fish = fish_objects[it.fish_id]
        oi = OrderItem(order_id=order.id, fish_id=it.fish_id, quantity=it.quantity)
        db.add(oi)
        if fish.stock is not None:
            fish.stock = fish.stock - it.quantity  # stock already validated above

    # BUG FIX #4 — Part C: Single commit for the entire order (atomic).
    # Previously there was a db.commit() inside the loop for every item,
    # which meant a crash mid-loop left partial stock deductions in the DB.
    db.commit()
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