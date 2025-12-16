from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Fish, Category
from schemas import FishCreate, FishOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=FishOut)
def create_fish(payload: FishCreate, db: Session = Depends(get_db)):
    if payload.category_id:
        cat = db.query(Category).filter(Category.category_id == payload.category_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
    f = Fish(**payload.dict())
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


@router.get("/", response_model=list[FishOut])
def list_fishes(db: Session = Depends(get_db)):
    return db.query(Fish).all()


@router.get("/{fish_id}", response_model=FishOut)
def get_fish(fish_id: int, db: Session = Depends(get_db)):
    f = db.query(Fish).filter(Fish.id == fish_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Fish not found")
    return f


@router.put("/{fish_id}", response_model=FishOut)
def update_fish(fish_id: int, payload: FishCreate, db: Session = Depends(get_db)):
    f = db.query(Fish).filter(Fish.id == fish_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Fish not found")
    for k, v in payload.dict().items():
        setattr(f, k, v)
    db.commit()
    db.refresh(f)
    return f


@router.delete("/{fish_id}")
def delete_fish(fish_id: int, db: Session = Depends(get_db)):
    f = db.query(Fish).filter(Fish.id == fish_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Fish not found")
    db.delete(f)
    db.commit()
    return {"detail": "Fish deleted"}
