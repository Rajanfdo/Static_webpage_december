from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ContactUs
from schemas import ContactUsCreate, ContactUsOut



router = APIRouter()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ContactUsOut)
def create_contact(payload: ContactUsCreate, db: Session = Depends(get_db)):
    contact = ContactUs(**payload.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/", response_model=list[ContactUsOut])
def list_contacts(db: Session = Depends(get_db)):
    return db.query(ContactUs).all()


@router.get("/{contact_id}", response_model=ContactUsOut)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(ContactUs).filter(ContactUs.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact
