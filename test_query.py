import sys
sys.path.insert(0, 'backend')

from models import Base, DeviceDB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///backend/sentinel.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()
try:
    devices = db.query(DeviceDB).all()
    print(f"Query successful! Found {len(devices)} devices")
    for d in devices:
        print(f"  - {d.hostname}: {d.device_id}")
except Exception as e:
    print(f"Query failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
