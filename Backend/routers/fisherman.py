from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database import SessionLocal
from models import FishermanSupply      # ← import from models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class FishItem(BaseModel):
    fish_name:    str
    quantity:     float
    price_per_kg: float
    condition:    Optional[str] = "fresh"

class SupplyRequest(BaseModel):
    fisherman_name: str
    phone:          str
    location:       Optional[str] = None
    contact_time:   Optional[str] = None
    notes:          Optional[str] = None
    items:          List[FishItem]

class SupplyOut(BaseModel):
    id:             int
    fisherman_name: str
    phone:          str
    status:         str

    class Config:
        from_attributes = True

@router.post("/supply", response_model=SupplyOut)
def submit_supply(payload: SupplyRequest, db: Session = Depends(get_db)):
    supply = FishermanSupply(
        fisherman_name = payload.fisherman_name,
        phone          = payload.phone,
        location       = payload.location,
        contact_time   = payload.contact_time,
        notes          = payload.notes,
        items          = [item.dict() for item in payload.items],
        status         = "pending"
    )
    db.add(supply)
    db.commit()
    db.refresh(supply)
    return supply

@router.get("/supply", response_model=List[SupplyOut])
def list_supplies(db: Session = Depends(get_db)):
    return db.query(FishermanSupply).order_by(FishermanSupply.id.desc()).all()