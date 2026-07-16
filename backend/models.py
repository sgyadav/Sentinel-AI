"""
UNIFIED PYDANTIC & SQLALCHEMY MODELS FOR SENTINEL AI
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import List, Optional, Dict

# ============= SQLALCHEMY BASE =============
Base = declarative_base()


# ============= SQLALCHEMY ORM MODELS =============

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="User")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmployeeDB(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    risk_score = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeviceDB(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), unique=True, nullable=False, index=True)
    hostname = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(15), nullable=False)
    mac_address = Column(String(17), default="")
    operating_system = Column(String(100), nullable=False)
    os_version = Column(String(50), default="")
    device_type = Column(String(50), default="Laptop")
    cpu_usage = Column(Float, default=0)
    ram_usage = Column(Float, default=0)
    disk_usage = Column(Float, default=0)
    status = Column(String(50), default="Online")
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AssignmentDB(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    assignment_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)


class ThreatDB(Base):
    __tablename__ = "threats"
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), default="default", nullable=False)
    threat_id = Column(String(100), unique=True, nullable=False, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    threat_name = Column(String(255), nullable=False)
    threat_type = Column(String(100), nullable=False)
    severity = Column(String(50), default="Medium")
    confidence = Column(Float, default=0)
    risk_score = Column(Float, default=0)
    detection_method = Column(String(100), default="")
    file_path = Column(Text, default="")
    file_hash = Column(String(255), default="")
    status = Column(String(50), default="Detected")
    action_taken = Column(Text, default="")
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProcessDB(Base):
    __tablename__ = "processes"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(255), default="", index=True)
    hostname = Column(String(255), nullable=False, index=True)
    pid = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    cpu_percent = Column(Float, default=0)
    memory_percent = Column(Float, default=0)
    username = Column(String(100), default="")
    classification = Column(String(30), default="Safe")
    risk_score = Column(Float, default=0)
    reason = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class USBEventDB(Base):
    __tablename__ = "usb_events"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(255), default="", index=True)
    action = Column(String(30), nullable=False)
    device = Column(String(255), nullable=False)
    hostname = Column(String(100), nullable=False)
    username = Column(String(100), default="Unknown")
    event_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SettingsDB(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(255), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NotificationDB(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String(100), unique=True, nullable=False)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OrganizationDB(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    organization_name = Column(String(255), nullable=False)
    admin_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    industry = Column(String(255), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LoginHistoryDB(Base):
    __tablename__ = "login_history"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, index=True)
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    logout_time = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(45), nullable=False)
    status = Column(String(50), nullable=False)
    reason = Column(String(255), nullable=True)
    session_duration = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EndpointSessionDB(Base):
    __tablename__ = "endpoint_sessions"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(255), nullable=False, index=True)
    hostname = Column(String(255), nullable=False, index=True)
    username = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), default="")
    login_time = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    logout_time = Column(DateTime(timezone=True), nullable=True)
    session_duration = Column(Integer, nullable=True)
    status = Column(String(50), default="Active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLogDB(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String(255), default="system")
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100), default="")
    resource_id = Column(String(255), default="")
    details = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============= PYDANTIC MODELS (Request/Response) =============

class LoginRequest(BaseModel):
    username: str
    password: str


class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    email: str
    phone: str = ""
    department: str
    designation: str = ""


class EmployeeResponse(BaseModel):
    employee_id: str
    name: str
    email: str
    phone: str
    department: str
    designation: str
    risk_score: float


class DeviceCreate(BaseModel):
    device_id: Optional[str] = None
    hostname: str
    ip_address: str
    mac_address: str = ""
    operating_system: str
    os_version: str = ""
    device_type: str = "Laptop"


class DeviceResponse(BaseModel):
    device_id: str
    hostname: str
    ip_address: str
    mac_address: str
    operating_system: str
    os_version: str
    device_type: str
    cpu_usage: float
    ram_usage: float
    disk_usage: float
    status: str
    last_heartbeat: Optional[str] = None


class AssignmentCreate(BaseModel):
    employee_id: str
    device_id: str


class AssignmentUpdate(BaseModel):
    employee_id: str
    device_id: str


class AssignmentResponse(BaseModel):
    id: int
    employee_id: str
    device_id: str
    assigned_date: Optional[str] = None
    is_active: bool


class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    username: str = "Unknown"
    agent_id: str = ""
    hostname: str = ""
    classification: str = "Safe"
    risk_score: float = 0
    reason: str = ""


class ProcessList(BaseModel):
    agent_id: str = ""
    hostname: str
    processes: List[ProcessInfo]


class Heartbeat(BaseModel):
    device_uuid: str = ""
    agent_id: str = ""
    hostname: str = "Unknown"
    username: str = "Unknown"
    ip_address: str = "0.0.0.0"
    operating_system: str = "Windows"
    cpu_usage: float = 0
    ram_usage: float = 0
    disk_usage: float = 0
    cpu_cores: int = 0
    total_ram: float = 0
    available_ram: float = 0
    boot_time: str = ""
    last_seen: str = ""
    status: str = "Online"
    mac_address: str = ""
    os_version: str = ""
    device_type: str = "Laptop"
    agent_version: str = ""


class ThreatResponse(BaseModel):
    threat_id: str
    device_id: str
    threat_name: str
    threat_type: str
    severity: str
    risk_score: float
    status: str
    detected_at: Optional[str] = None


class SettingsUpdate(BaseModel):
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_email: str = ""
    smtp_password: str = ""
    admin_email: str = ""


class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    message: str


class EndpointSessionEvent(BaseModel):
    agent_id: str = ""
    hostname: str
    username: str
    ip_address: str = ""
    action: str = Field(..., pattern=r'^(login|logout)$')
    event_time: Optional[str] = None


class SecurityEvent(BaseModel):
    """Security event model"""
    hostname: str = Field(..., min_length=1, max_length=255)
    event_type: str = Field(..., min_length=1, max_length=255)
    severity: str = Field(..., pattern=r'^(Low|Medium|High|Critical)$')
    description: str = Field(..., min_length=1, max_length=1000)

    @validator('event_type')
    def validate_event_type(cls, v):
        valid_types = {
            "Failed Login", "Brute Force", "Malware", "Ransomware",
            "USB Attack", "Port Scan", "Privilege Escalation",
            "Data Exfiltration", "Command & Control", "DNS Tunneling"
        }
        if v not in valid_types:
            raise ValueError(f"Invalid event type")
        return v
