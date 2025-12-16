from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Address, Login
from schemas import AddressCreate, AddressOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AddressOut)
def create_address(address: AddressCreate, db: Session = Depends(get_db)):
    login = db.query(Login).filter(Login.login_id == address.login_id).first()
    if not login:
        raise HTTPException(status_code=404, detail="Login not found")
    obj = Address(**address.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=list[AddressOut])
def list_addresses(db: Session = Depends(get_db)):
    return db.query(Address).all()
