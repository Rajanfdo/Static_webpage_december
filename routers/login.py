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
    login = Login(username=payload.username, email=payload.email, password=payload.password)
    db.add(login)
    db.commit()
    db.refresh(login)
    return login

    
