from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from schemas import UserCreate, UserOut, UserLogin

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    # Prevent duplicate email registrations
    existing = db.query(Users).filter(Users.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = Users(**payload.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(Users).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# BUG FIX #6: Added a proper login endpoint.
# Previously the frontend fetched GET /api/users/ (all users) and searched
# client-side — this exposed every user's data to the browser.
# Now the frontend POSTs { email, password } here and only gets back
# the matching user (or a 401 error).
@router.post("/login", response_model=UserOut)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email")
    if user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid password")
    return user