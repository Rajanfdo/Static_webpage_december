# login_router.py  (or wherever this router lives — replace your existing file)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Login
from schemas import LoginCreate, LoginOut
from pydantic import BaseModel

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Schema for login request ──────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str


# ── Schema for login response (includes role so frontend can check admin) ─────
class LoginResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str          # ← this is what the frontend reads to show/hide Admin button

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/login/auth   →   check email + password, return user with role
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/auth", response_model=LoginResponse)
def do_login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Login).filter(Login.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email.")

    # Plain-text comparison (upgrade to bcrypt when ready — see note below)
    if user.password != payload.password:
        raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")

    return user


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/login/       →   register a new user
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/", response_model=LoginOut)
def create_login(payload: LoginCreate, db: Session = Depends(get_db)):
    if payload.email:
        existing = db.query(Login).filter(Login.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered.")

    login = Login(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role="customer"          # always default to customer on self-registration
    )
    db.add(login)
    db.commit()
    db.refresh(login)
    return login


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/login/        →   list all users (admin use only ideally)
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=list[LoginOut])
def list_logins(db: Session = Depends(get_db)):
    return db.query(Login).all()


# ─────────────────────────────────────────────────────────────────────────────
# NOTE: Password hashing (add this when ready)
# ─────────────────────────────────────────────────────────────────────────────
# pip install bcrypt
#
# import bcrypt
#
# def hash_password(plain: str) -> str:
#     return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
#
# def verify_password(plain: str, hashed: str) -> bool:
#     return bcrypt.checkpw(plain.encode(), hashed.encode())
#
# Then in do_login replace the plain comparison with:
#   if not verify_password(payload.password, user.password):
#
# And in create_login:
#   login = Login(..., password=hash_password(payload.password), ...)