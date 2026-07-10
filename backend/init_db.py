"""Initialize database with admin user"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from auth.password import hash_password

DATABASE_URL = "sqlite:///./sentinel.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Simple Base for initialization
Base = declarative_base()

class UserSimple(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="Admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def init_database():
    """Initialize database"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables created")
        
        # Create admin user
        db = SessionLocal()
        try:
            # Check if admin exists
            admin = db.query(UserSimple).filter(UserSimple.username == "admin").first()
            if admin:
                print("[OK] Admin user already exists")
                return
            
            # Create admin
            hashed_password = hash_password("Admin1234")
            admin_user = UserSimple(
                username="admin",
                email="admin@sentinelai.local",
                password=hashed_password,
                role="Admin",
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            print("[OK] Admin user created successfully")
            print("[INFO] Username: admin")
            print("[INFO] Password: Admin1234")
            
        except Exception as e:
            print(f"[ERROR] Error creating admin user: {str(e)}")
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    init_database()
