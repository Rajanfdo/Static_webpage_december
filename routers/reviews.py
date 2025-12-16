from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Review, Users, Fish
from schemas import ReviewCreate, ReviewOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ReviewOut)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)):
    if not db.query(Users).filter(Users.id == payload.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    if not db.query(Fish).filter(Fish.id == payload.fish_id).first():
        raise HTTPException(status_code=404, detail="Fish not found")
    r = Review(user_id=payload.user_id, fish_id=payload.fish_id, rating=payload.rating)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("/", response_model=list[ReviewOut])
def list_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()
