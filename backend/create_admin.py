import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from auth.password import hash_password

DATABASE_URL = "sqlite:///./sentinel.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="User")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Base.metadata.create_all(bind=engine)

db = SessionLocal()
admin = db.query(UserDB).filter(UserDB.username == "admin").first()
if not admin:
    initial_password = (
        os.getenv("SENTINEL_INITIAL_ADMIN_PASSWORD")
        or os.getenv("INITIAL_ADMIN_PASSWORD")
        or os.getenv("ADMIN_PASSWORD")
    )
    if not initial_password:
        raise SystemExit("Set SENTINEL_INITIAL_ADMIN_PASSWORD before creating the admin account")
    hashed_pass = hash_password(initial_password)
    admin_user = UserDB(
        username="admin",
        email="admin@sentinelai.local",
        password=hashed_pass,
        role="Admin",
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    print("[OK] Admin user created")
else:
    print(f"[OK] Admin already exists")
db.close()
