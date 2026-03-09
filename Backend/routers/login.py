from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Login
from schemas import LoginCreate, LoginOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=LoginOut)
def create_login(payload: LoginCreate, db: Session = Depends(get_db)):
    # BUG FIX #7: Prevent duplicate email registrations in the Login table.
    if payload.email:
        existing = db.query(Login).filter(Login.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    login = Login(
        username=payload.username,
        email=payload.email,
        password=payload.password
    )
    db.add(login)
    db.commit()
    db.refresh(login)
    return login


@router.get("/", response_model=list[LoginOut])
def list_logins(db: Session = Depends(get_db)):
    return db.query(Login).all()