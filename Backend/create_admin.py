import sys
import os

from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Users

def create_admin():
    db = SessionLocal()
    try:
        email = "admin@freshcoastal.com"
        password = "admin"
        print("Checking if admin exists...")
        admin = db.query(Users).filter(Users.email == email).first()
        if admin:
            if admin.role != "admin":
                admin.role = "admin"
                admin.password = password
                db.commit()
                print(f"Updated existing user {email} to admin role with new password '{password}'.")
            else:
                admin.password = password
                db.commit()
                print(f"Admin already exists. Password reset to '{password}'.")
        else:
            new_admin = Users(
                name="System Admin",
                email=email,
                password=password,
                role="admin",
                phone="",
                address=""
            )
            db.add(new_admin)
            db.commit()
            print(f"Created new admin user. Email: {email}, Password: {password}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_admin()
