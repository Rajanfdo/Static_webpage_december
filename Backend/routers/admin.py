from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Users, Fish, Orders, Category
from schemas import FishCreate, FishOut, OrderOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/login")
def admin_login(email: str, password: str, db: Session = Depends(get_db)):
    admin = db.query(Users).filter(Users.email == email, Users.role == "admin").first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if admin.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Admin login successful", "admin_id": admin.id}



@router.post("/fish", response_model=FishOut)
def admin_add_fish(payload: FishCreate, db: Session = Depends(get_db)):
    if payload.category_id:
        cat = db.query(Category).filter(Category.category_id == payload.category_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

    fish = Fish(**payload.dict())
    db.add(fish)
    db.commit()
    db.refresh(fish)

    return fish



@router.put("/fish/{fish_id}", response_model=FishOut)
def admin_update_fish(fish_id: int, payload: FishCreate, db: Session = Depends(get_db)):
    fish = db.query(Fish).filter(Fish.id == fish_id).first()

    if not fish:
        raise HTTPException(status_code=404, detail="Fish not found")

    for key, value in payload.dict().items():
        setattr(fish, key, value)

    db.commit()
    db.refresh(fish)
    return fish


@router.delete("/fish/{fish_id}")
def admin_delete_fish(fish_id: int, db: Session = Depends(get_db)):
    fish = db.query(Fish).filter(Fish.id == fish_id).first()

    if not fish:
        raise HTTPException(status_code=404, detail="Fish not found")

    db.delete(fish)
    db.commit()
    return {"message": "Fish deleted successfully"}



@router.get("/fish", response_model=list[FishOut])
def admin_list_fishes(db: Session = Depends(get_db)):
    return db.query(Fish).all()



@router.get("/orders", response_model=list[OrderOut])
def admin_list_orders(db: Session = Depends(get_db)):
    return db.query(Orders).all()




