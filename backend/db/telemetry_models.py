from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime

from .database import Base


class TelemetryDB(Base):

    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)

    hostname = Column(String, index=True)

    username = Column(String)

    ip_address = Column(String)

    operating_system = Column(String)

    cpu_usage = Column(Float)

    ram_usage = Column(Float)

    disk_usage = Column(Float)

    status = Column(String)

    raw_json = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)