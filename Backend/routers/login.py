# login_router.py — replace your existing file with this

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Login, Users       # ← imports BOTH models
from schemas import LoginCreate, LoginOut
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/login/auth  →  checks Users table first, then Login table
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/auth", response_model=LoginResponse)
def do_login(payload: LoginRequest, db: Session = Depends(get_db)):

    # 1️⃣  Check Users table first (where create_admin.py stores admin)
    user_obj = None
    try:
        user_obj = db.query(Users).filter(Users.email == payload.email).first()
        if user_obj:
            if user_obj.password != payload.password:
                raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")
            # Return in standard format
            return LoginResponse(
                id       = user_obj.id,
                username = getattr(user_obj, "name", None) or getattr(user_obj, "username", None) or user_obj.email,
                email    = user_obj.email,
                role     = getattr(user_obj, "role", "customer") or "customer"
            )
    except HTTPException:
        raise
    except Exception:
        pass   # Users table might not exist — fall through to Login table

    # 2️⃣  Check Login table
    login_obj = None
    try:
        login_obj = db.query(Login).filter(Login.email == payload.email).first()
        if login_obj:
            if login_obj.password != payload.password:
                raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")
            return LoginResponse(
                id       = login_obj.id,
                username = getattr(login_obj, "username", None) or login_obj.email,
                email    = login_obj.email,
                role     = getattr(login_obj, "role", "customer") or "customer"
            )
    except HTTPException:
        raise
    except Exception:
        pass

    # 3️⃣  Not found in either table
    raise HTTPException(status_code=404, detail="No account found with this email.")


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/login/  →  register new user (saves to Login table)
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/", response_model=LoginOut)
def create_login(payload: LoginCreate, db: Session = Depends(get_db)):
    # Check both tables for duplicate email
    try:
        if db.query(Users).filter(Users.email == payload.email).first():
            raise HTTPException(status_code=400, detail="Email already registered.")
    except HTTPException:
        raise
    except Exception:
        pass

    try:
        if db.query(Login).filter(Login.email == payload.email).first():
            raise HTTPException(status_code=400, detail="Email already registered.")
    except HTTPException:
        raise
    except Exception:
        pass

    login = Login(
        username = payload.username,
        email    = payload.email,
        password = payload.password,
        role     = "customer"
    )
    db.add(login)
    db.commit()
    db.refresh(login)
    return login


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/login/  →  list all login users
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=list[LoginOut])
def list_logins(db: Session = Depends(get_db)):
    return db.query(Login).all()