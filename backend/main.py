"""
SENTINEL AI - COMPLETE BACKEND WITH LIVE MONITORING, ADMIN SETTINGS & EMAIL
"""

import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============= DATABASE SETUP =============
DATABASE_URL = "sqlite:///./sentinel.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= MODELS =============
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
    employee_id = Column(String(50), unique=True, nullable=False)
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
    id = Column(Integer, primary_key=True)
    device_id = Column(String(100), unique=True, nullable=False)
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(15), nullable=False)
    mac_address = Column(String(17))
    operating_system = Column(String(100), nullable=False)
    os_version = Column(String(50))
    device_type = Column(String(50), default="Laptop")
    cpu_usage = Column(Float, default=0)
    ram_usage = Column(Float, default=0)
    disk_usage = Column(Float, default=0)
    status = Column(String(50), default="Online")
    threat_count = Column(Integer, default=0)
    last_heartbeat = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AssignmentDB(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), nullable=False)
    device_id = Column(String(100), nullable=False)
    assignment_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class ThreatDB(Base):
    __tablename__ = "threats"
    id = Column(Integer, primary_key=True)
    threat_id = Column(String(100), unique=True, nullable=False)
    device_id = Column(String(100), nullable=False)
    threat_name = Column(String(255), nullable=False)
    threat_type = Column(String(100), nullable=False)
    severity = Column(String(50), default="Medium")
    risk_score = Column(Float, default=0)
    status = Column(String(50), default="Detected")
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

class SettingsDB(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(255), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class NotificationDB(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    notification_id = Column(String(100), unique=True, nullable=False)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ============= PYDANTIC MODELS =============
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

class DeviceCreate(BaseModel):
    hostname: str
    ip_address: str
    mac_address: str = ""
    operating_system: str
    os_version: str = ""
    device_type: str = "Laptop"

class AssignmentCreate(BaseModel):
    employee_id: str
    device_id: str


class AssignmentUpdate(BaseModel):
    employee_id: str
    device_id: str

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

# ============= UTILITY FUNCTIONS =============
def hash_password(password: str) -> str:
    return "sha256:" + hashlib.sha256(password.encode()).hexdigest()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============= FASTAPI APP =============
app = FastAPI(title="SENTINEL AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
    
    db = SessionLocal()
    try:
        admin = db.query(UserDB).filter(UserDB.username == "admin").first()
        if not admin:
            admin_user = UserDB(
                username="admin",
                email="admin@sentinelai.local",
                password=hash_password("Admin1234"),
                role="Admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            logger.info("Admin user created")
    finally:
        db.close()

# ============= AUTH ENDPOINTS =============
@app.post("/auth/login")
def login(request: LoginRequest, db = Depends(get_db)):
    logger.info(f"Login attempt for user: {request.username}")
    user = db.query(UserDB).filter(UserDB.username == request.username).first()
    
    if not user:
        logger.error(f"User not found: {request.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    hashed_input = hash_password(request.password)
    
    if user.password != hashed_input:
        logger.error(f"Password mismatch for user: {request.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    logger.info(f"User {request.username} logged in successfully")
    return {
        "success": True,
        "access_token": f"token_{user.username}_{int(datetime.now().timestamp())}",
        "user": {"username": user.username, "role": user.role, "email": user.email}
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# ============= EMPLOYEE ENDPOINTS =============
@app.post("/employees")
def create_employee(emp: EmployeeCreate, db = Depends(get_db)):
    new_emp = EmployeeDB(**emp.dict())
    db.add(new_emp)
    db.commit()
    return {"success": True, "employee_id": emp.employee_id}

@app.get("/employees")
def get_employees(db = Depends(get_db)):
    employees = db.query(EmployeeDB).all()
    return {
        "total": len(employees),
        "employees": [
            {
                "employee_id": e.employee_id,
                "name": e.name,
                "email": e.email,
                "phone": e.phone,
                "department": e.department,
                "designation": e.designation,
                "risk_score": e.risk_score
            }
            for e in employees
        ]
    }

@app.put("/employees/{employee_id}")
def update_employee(employee_id: str, emp: EmployeeCreate, db = Depends(get_db)):
    employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    for key, value in emp.dict().items():
        if key != "employee_id":
            setattr(employee, key, value)
    
    employee.updated_at = datetime.utcnow()
    db.commit()
    return {"success": True, "message": "Employee updated"}

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: str, db = Depends(get_db)):
    employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db.delete(employee)
    db.commit()
    return {"success": True, "message": "Employee deleted"}

# ============= DEVICE ENDPOINTS =============
@app.post("/devices")
def create_device(dev: DeviceCreate, db = Depends(get_db)):
    device_id = f"{dev.hostname}_{int(datetime.now().timestamp())}"
    new_dev = DeviceDB(device_id=device_id, **dev.dict())
    db.add(new_dev)
    db.commit()
    return {"success": True, "device_id": device_id}

@app.get("/devices")
def get_devices(db = Depends(get_db)):
    devices = db.query(DeviceDB).all()
    return {
        "total": len(devices),
        "devices": [
            {
                "device_id": d.device_id,
                "hostname": d.hostname,
                "ip_address": d.ip_address,
                "mac_address": d.mac_address,
                "operating_system": d.operating_system,
                "os_version": d.os_version,
                "device_type": d.device_type,
                "cpu_usage": d.cpu_usage,
                "ram_usage": d.ram_usage,
                "disk_usage": d.disk_usage,
                "status": d.status,
                "threat_count": d.threat_count
            }
            for d in devices
        ]
    }

@app.put("/devices/{device_id}")
def update_device(device_id: str, dev: DeviceCreate, db = Depends(get_db)):
    device = db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    for key, value in dev.dict().items():
        setattr(device, key, value)
    
    device.updated_at = datetime.utcnow()
    db.commit()
    return {"success": True, "message": "Device updated"}

@app.delete("/devices/{device_id}")
def delete_device(device_id: str, db = Depends(get_db)):
    device = db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(device)
    db.commit()
    return {"success": True, "message": "Device deleted"}

# ============= ASSIGNMENT ENDPOINTS =============
@app.post("/assignments")
def create_assignment(assign: AssignmentCreate, db = Depends(get_db)):
    new_assign = AssignmentDB(**assign.dict())
    db.add(new_assign)
    db.commit()
    return {"success": True, "message": "Device assigned"}

@app.get("/assignments")
def get_assignments(db = Depends(get_db)):
    assignments = db.query(AssignmentDB).all()
    return {
    "total": len(assignments),
    "assignments": [
        {
            "id": a.id,
            "employee_id": a.employee_id,
            "device_id": a.device_id,
            "assigned_date": a.assignment_date.isoformat() if a.assignment_date else None,
            "is_active": a.is_active
        }
        for a in assignments
    ]
}

@app.put("/assignments/{assignment_id}")
def update_assignment(
    assignment_id: int,
    assignment: AssignmentUpdate,
    db = Depends(get_db)
):
    existing = db.query(AssignmentDB).filter(
        AssignmentDB.id == assignment_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Assignment not found")

    existing.employee_id = assignment.employee_id
    existing.device_id = assignment.device_id

    db.commit()
    db.refresh(existing)

    return {
        "success": True,
        "message": "Assignment updated successfully"
    }

@app.delete("/assignments/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db = Depends(get_db)
):
    assignment = db.query(AssignmentDB).filter(
        AssignmentDB.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    db.delete(assignment)
    db.commit()

    return {
        "success": True,
        "message": "Assignment deleted successfully"
    }

# ============= THREAT ENDPOINTS =============
@app.get("/threats")
def get_threats(db = Depends(get_db)):
    threats = db.query(ThreatDB).all()
    return {
        "total": len(threats),
        "threats": [
            {
                "threat_id": t.threat_id,
                "device_id": t.device_id,
                "threat_name": t.threat_name,
                "threat_type": t.threat_type,
                "severity": t.severity,
                "risk_score": t.risk_score,
                "status": t.status,
                "detected_at": t.detected_at.isoformat() if t.detected_at else None
            }
            for t in threats
        ]
    }

# ============= DASHBOARD ENDPOINT =============
@app.get("/dashboard")
def get_dashboard(db = Depends(get_db)):
    emp_count = db.query(EmployeeDB).count()
    dev_count = db.query(DeviceDB).count()
    threat_count = db.query(ThreatDB).count()
    
    employees = db.query(EmployeeDB).all()
    emp_monitoring = []
    for emp in employees:
        emp_monitoring.append({
            "employee_id": emp.employee_id,
            "name": emp.name,
            "risk_score": emp.risk_score,
            "status": "Active" if emp.risk_score < 50 else "Alert",
            "email": emp.email
        })
    
    return {
        "summary": {
            "total_employees": emp_count,
            "total_devices": dev_count,
            "total_threats": threat_count,
            "total_incidents": 0
        },
        "employee_monitoring": emp_monitoring,
        "status": "operational"
    }

# ============= ADMIN SETTINGS ENDPOINTS =============
@app.get("/settings")
def get_settings(db = Depends(get_db)):
    settings = db.query(SettingsDB).all()
    settings_dict = {s.setting_key: s.setting_value for s in settings}
    return {
        "smtp_server": settings_dict.get("smtp_server", ""),
        "smtp_port": int(settings_dict.get("smtp_port", "587")),
        "smtp_email": settings_dict.get("smtp_email", ""),
        "smtp_password": "*" * min(8, len(settings_dict.get("smtp_password", ""))),
        "admin_email": settings_dict.get("admin_email", "")
    }

@app.post("/settings")
def update_settings(settings: SettingsUpdate, db = Depends(get_db)):
    db.query(SettingsDB).delete()
    
    settings_list = [
        SettingsDB(setting_key="smtp_server", setting_value=settings.smtp_server),
        SettingsDB(setting_key="smtp_port", setting_value=str(settings.smtp_port)),
        SettingsDB(setting_key="smtp_email", setting_value=settings.smtp_email),
        SettingsDB(setting_key="smtp_password", setting_value=settings.smtp_password),
        SettingsDB(setting_key="admin_email", setting_value=settings.admin_email),
    ]
    
    for setting in settings_list:
        db.add(setting)
    
    db.commit()
    return {"success": True, "message": "Settings updated successfully"}

@app.post("/test-email")
def test_email(request: SendEmailRequest, db = Depends(get_db)):
    try:
        settings = db.query(SettingsDB).all()
        settings_dict = {s.setting_key: s.setting_value for s in settings}
        
        smtp_server = settings_dict.get("smtp_server", "")
        smtp_port = int(settings_dict.get("smtp_port", "587"))
        smtp_email = settings_dict.get("smtp_email", "")
        smtp_password = settings_dict.get("smtp_password", "")
        
        if not all([smtp_server, smtp_email, smtp_password]):
            return {"success": False, "message": "Email settings not configured"}
        
        msg = MIMEMultipart()
        msg["From"] = smtp_email
        msg["To"] = request.to_email
        msg["Subject"] = request.subject
        msg.attach(MIMEText(request.message, "html"))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return {"success": True, "message": "Test email sent successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/send-email")
def send_email_notification(request: SendEmailRequest, db = Depends(get_db)):
    try:
        settings = db.query(SettingsDB).all()
        settings_dict = {s.setting_key: s.setting_value for s in settings}
        
        smtp_server = settings_dict.get("smtp_server", "")
        smtp_port = int(settings_dict.get("smtp_port", "587"))
        smtp_email = settings_dict.get("smtp_email", "")
        smtp_password = settings_dict.get("smtp_password", "")
        
        if not all([smtp_server, smtp_email, smtp_password]):
            return {"success": False, "message": "Email settings not configured"}
        
        msg = MIMEMultipart()
        msg["From"] = smtp_email
        msg["To"] = request.to_email
        msg["Subject"] = request.subject
        msg.attach(MIMEText(request.message, "html"))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()
        
        notification = NotificationDB(
            notification_id=f"notif_{int(datetime.now().timestamp())}",
            recipient_email=request.to_email,
            subject=request.subject,
            message=request.message,
            status="Sent"
        )
        db.add(notification)
        db.commit()
        
        return {"success": True, "message": "Email sent successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/notifications")
def get_notifications(db = Depends(get_db)):
    notifications = db.query(NotificationDB).order_by(NotificationDB.created_at.desc()).limit(50).all()
    return {
        "total": len(notifications),
        "notifications": [
            {
                "notification_id": n.notification_id,
                "recipient_email": n.recipient_email,
                "subject": n.subject,
                "status": n.status,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in notifications
        ]
    }

@app.get("/employee-monitoring")
def get_employee_monitoring(db = Depends(get_db)):
    employees = db.query(EmployeeDB).all()
    monitoring_data = []
    
    for emp in employees:
        assignments = db.query(AssignmentDB).filter(AssignmentDB.employee_id == emp.employee_id).all()
        device_count = len(assignments)
        
        device_ids = [a.device_id for a in assignments]
        threats = db.query(ThreatDB).filter(ThreatDB.device_id.in_(device_ids)).all() if device_ids else []
        threat_count = len(threats)
        
        monitoring_data.append({
            "employee_id": emp.employee_id,
            "name": emp.name,
            "email": emp.email,
            "department": emp.department,
            "device_count": device_count,
            "threat_count": threat_count,
            "risk_score": emp.risk_score,
            "status": "Secure" if threat_count == 0 else "Alert" if threat_count <= 2 else "Critical",
            "color": "#10b981" if threat_count == 0 else "#f59e0b" if threat_count <= 2 else "#ef4444"
        })
    
    return {"total": len(monitoring_data), "employees": monitoring_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
