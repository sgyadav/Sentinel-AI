"""
SENTINEL AI - COMPLETE REAL PRODUCTION BACKEND
All features: Real monitoring, threat detection, device assignment, organization management
"""

import os
import logging
import secrets
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

# Database
from db.database import get_db, init_db
from db.models import (
    OrganizationDB, UserDB, EmployeeDB, DeviceDB, DeviceAssignmentDB,
    ThreatDB, ScanResultDB, MonitoringDataDB, IncidentDB, ActivityLogDB
)

# Auth
from auth.auth_routes import router as auth_router
from services.auth_service import AuthService
from core.security import get_current_user

# Threat Detection
from threat_detection import RealThreatDetector, ThreatAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SENTINEL AI - Real Cyber Defense",
    description="Production Real-Time Threat Detection",
    version="2.0.0",
    docs_url="/docs"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup
@app.on_event("startup")
async def startup():
    try:
        init_db()
        logger.info("SENTINEL AI STARTED - REAL CYBER DEFENSE ACTIVE")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")

app.include_router(auth_router)

# ========================
# PYDANTIC MODELS
# ========================

class OrganizationCreate(BaseModel):
    org_id: str
    name: str
    email: EmailStr
    phone: str = ""
    address: str = ""
    industry: str = ""
    website: str = ""

class OrganizationResponse(BaseModel):
    org_id: str
    name: str
    email: str
    is_active: bool
    employees_count: int
    devices_count: int

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    email: str
    phone: str = ""
    department: str
    designation: str
    manager_id: str = ""

class EmployeeUpdate(BaseModel):
    name: str = None
    email: str = None
    phone: str = None
    department: str = None
    designation: str = None

class DeviceCreate(BaseModel):
    hostname: str
    ip_address: str
    mac_address: str = ""
    operating_system: str
    os_version: str = ""
    device_type: str = "Laptop"
    cpu_cores: int = 0
    total_ram: int = 0
    total_disk: int = 0

class DeviceUpdate(BaseModel):
    ip_address: str = None
    mac_address: str = None
    operating_system: str = None
    os_version: str = None

class DeviceAssignmentCreate(BaseModel):
    employee_id: str
    device_id: str

class PasswordReset(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# ========================
# HEALTH ENDPOINTS
# ========================

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
def home():
    return {"status": "SENTINEL AI Running", "version": "2.0.0"}

# ========================
# ORGANIZATION ENDPOINTS
# ========================

@app.post("/organizations", response_model=dict)
def register_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    """Register new organization"""
    try:
        # Check if exists
        existing = db.query(OrganizationDB).filter(OrganizationDB.org_id == org.org_id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Organization already exists")
        
        new_org = OrganizationDB(
            org_id=org.org_id,
            name=org.name,
            email=org.email,
            phone=org.phone,
            address=org.address,
            industry=org.industry,
            website=org.website
        )
        
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        
        logger.info(f"Organization registered: {org.org_id}")
        return {
            "success": True,
            "message": "Organization registered successfully",
            "org_id": org.org_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organizations/{org_id}", response_model=dict)
def get_organization(org_id: str, db: Session = Depends(get_db)):
    """Get organization details"""
    try:
        org = db.query(OrganizationDB).filter(OrganizationDB.org_id == org_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return {
            "org_id": org.org_id,
            "name": org.name,
            "email": org.email,
            "industry": org.industry,
            "employees_count": org.employees_count,
            "devices_count": org.devices_count,
            "is_active": org.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# EMPLOYEE ENDPOINTS
# ========================

@app.post("/employees", response_model=dict)
def create_employee(emp: EmployeeCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create employee"""
    try:
        org_id = current_user.get("org_id")
        
        new_emp = EmployeeDB(
            org_id=org_id,
            employee_id=emp.employee_id,
            name=emp.name,
            email=emp.email,
            phone=emp.phone,
            department=emp.department,
            designation=emp.designation,
            manager_id=emp.manager_id
        )
        
        db.add(new_emp)
        db.commit()
        db.refresh(new_emp)
        
        logger.info(f"Employee created: {emp.employee_id}")
        return {
            "success": True,
            "message": "Employee created",
            "employee_id": emp.employee_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/employees", response_model=dict)
def get_employees(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all employees"""
    try:
        org_id = current_user.get("org_id")
        employees = db.query(EmployeeDB).filter(EmployeeDB.org_id == org_id).all()
        
        emp_list = [
            {
                "employee_id": e.employee_id,
                "name": e.name,
                "email": e.email,
                "department": e.department,
                "designation": e.designation,
                "risk_score": e.risk_score,
                "risk_level": e.risk_level,
                "is_active": e.is_active
            }
            for e in employees
        ]
        
        return {"total": len(emp_list), "employees": emp_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/employees/{employee_id}", response_model=dict)
def update_employee(employee_id: str, emp: EmployeeUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update employee"""
    try:
        org_id = current_user.get("org_id")
        employee = db.query(EmployeeDB).filter(
            (EmployeeDB.org_id == org_id) & (EmployeeDB.employee_id == employee_id)
        ).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        if emp.name:
            employee.name = emp.name
        if emp.email:
            employee.email = emp.email
        if emp.phone:
            employee.phone = emp.phone
        if emp.department:
            employee.department = emp.department
        if emp.designation:
            employee.designation = emp.designation
        
        employee.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Employee updated: {employee_id}")
        return {"success": True, "message": "Employee updated"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/employees/{employee_id}", response_model=dict)
def delete_employee(employee_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete employee"""
    try:
        org_id = current_user.get("org_id")
        employee = db.query(EmployeeDB).filter(
            (EmployeeDB.org_id == org_id) & (EmployeeDB.employee_id == employee_id)
        ).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        db.delete(employee)
        db.commit()
        
        logger.info(f"Employee deleted: {employee_id}")
        return {"success": True, "message": "Employee deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# DEVICE ENDPOINTS
# ========================

@app.post("/devices", response_model=dict)
def create_device(dev: DeviceCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Register device"""
    try:
        org_id = current_user.get("org_id")
        device_id = f"{org_id}-{dev.hostname}"
        
        new_device = DeviceDB(
            org_id=org_id,
            device_id=device_id,
            hostname=dev.hostname,
            ip_address=dev.ip_address,
            mac_address=dev.mac_address,
            operating_system=dev.operating_system,
            os_version=dev.os_version,
            device_type=dev.device_type,
            cpu_cores=dev.cpu_cores,
            total_ram=dev.total_ram,
            total_disk=dev.total_disk,
            last_heartbeat=datetime.utcnow()
        )
        
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        
        logger.info(f"Device registered: {device_id}")
        return {
            "success": True,
            "message": "Device registered",
            "device_id": device_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices", response_model=dict)
def get_devices(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all devices"""
    try:
        org_id = current_user.get("org_id")
        devices = db.query(DeviceDB).filter(DeviceDB.org_id == org_id).all()
        
        dev_list = [
            {
                "device_id": d.device_id,
                "hostname": d.hostname,
                "ip_address": d.ip_address,
                "operating_system": d.operating_system,
                "cpu_usage": d.cpu_usage,
                "ram_usage": d.ram_usage,
                "disk_usage": d.disk_usage,
                "status": d.status,
                "threat_count": d.threat_count,
                "last_heartbeat": d.last_heartbeat.isoformat() if d.last_heartbeat else None
            }
            for d in devices
        ]
        
        return {"total": len(dev_list), "devices": dev_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/devices/{device_id}", response_model=dict)
def update_device(device_id: str, dev: DeviceUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update device"""
    try:
        org_id = current_user.get("org_id")
        device = db.query(DeviceDB).filter(
            (DeviceDB.org_id == org_id) & (DeviceDB.device_id == device_id)
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        if dev.ip_address:
            device.ip_address = dev.ip_address
        if dev.mac_address:
            device.mac_address = dev.mac_address
        if dev.operating_system:
            device.operating_system = dev.operating_system
        if dev.os_version:
            device.os_version = dev.os_version
        
        device.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Device updated: {device_id}")
        return {"success": True, "message": "Device updated"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/devices/{device_id}", response_model=dict)
def delete_device(device_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete device"""
    try:
        org_id = current_user.get("org_id")
        device = db.query(DeviceDB).filter(
            (DeviceDB.org_id == org_id) & (DeviceDB.device_id == device_id)
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        db.delete(device)
        db.commit()
        
        logger.info(f"Device deleted: {device_id}")
        return {"success": True, "message": "Device deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# DEVICE ASSIGNMENT ENDPOINTS
# ========================

@app.post("/assignments", response_model=dict)
def assign_device(assignment: DeviceAssignmentCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Assign device to employee"""
    try:
        org_id = current_user.get("org_id")
        
        # Verify employee exists
        emp = db.query(EmployeeDB).filter(
            (EmployeeDB.org_id == org_id) & (EmployeeDB.employee_id == assignment.employee_id)
        ).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Verify device exists
        dev = db.query(DeviceDB).filter(
            (DeviceDB.org_id == org_id) & (DeviceDB.device_id == assignment.device_id)
        ).first()
        if not dev:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Create assignment
        new_assignment = DeviceAssignmentDB(
            org_id=org_id,
            employee_id=assignment.employee_id,
            device_id=assignment.device_id,
            is_active=True
        )
        
        db.add(new_assignment)
        db.commit()
        
        logger.info(f"Device assigned: {assignment.device_id} -> {assignment.employee_id}")
        return {
            "success": True,
            "message": "Device assigned to employee"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assignments", response_model=dict)
def get_assignments(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all device assignments"""
    try:
        org_id = current_user.get("org_id")
        assignments = db.query(DeviceAssignmentDB).filter(DeviceAssignmentDB.org_id == org_id).all()
        
        assign_list = [
            {
                "employee_id": a.employee_id,
                "device_id": a.device_id,
                "assigned_date": a.assignment_date.isoformat(),
                "is_active": a.is_active
            }
            for a in assignments
        ]
        
        return {"total": len(assign_list), "assignments": assign_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# THREAT & MONITORING ENDPOINTS
# ========================

@app.post("/scan/{device_id}", response_model=dict)
def start_threat_scan(device_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    """Start real threat scan"""
    try:
        org_id = current_user.get("org_id")
        device = db.query(DeviceDB).filter(
            (DeviceDB.org_id == org_id) & (DeviceDB.device_id == device_id)
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Run threat detection in background
        background_tasks.add_task(RealThreatDetector.scan_device_real_time, device.hostname, device.ip_address)
        
        return {
            "success": True,
            "message": "Threat scan started",
            "device_id": device_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/threats", response_model=dict)
def get_threats(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detected threats"""
    try:
        org_id = current_user.get("org_id")
        threats = db.query(ThreatDB).filter(ThreatDB.org_id == org_id).all()
        
        threat_list = [
            {
                "threat_id": t.threat_id,
                "device_id": t.device_id,
                "threat_name": t.threat_name,
                "threat_type": t.threat_type,
                "severity": t.severity,
                "confidence": t.confidence,
                "risk_score": t.risk_score,
                "status": t.status,
                "detected_at": t.detected_at.isoformat()
            }
            for t in threats
        ]
        
        return {"total": len(threat_list), "threats": threat_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/{device_id}", response_model=dict)
def get_monitoring_data(device_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get real-time monitoring data"""
    try:
        org_id = current_user.get("org_id")
        device = db.query(DeviceDB).filter(
            (DeviceDB.org_id == org_id) & (DeviceDB.device_id == device_id)
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Get latest monitoring data
        monitoring = db.query(MonitoringDataDB).filter(
            MonitoringDataDB.device_id == device_id
        ).order_by(MonitoringDataDB.timestamp.desc()).first()
        
        if monitoring:
            return {
                "device_id": device_id,
                "cpu_usage": monitoring.cpu_usage,
                "ram_usage": monitoring.ram_usage,
                "disk_usage": monitoring.disk_usage,
                "network_in": monitoring.network_in,
                "network_out": monitoring.network_out,
                "timestamp": monitoring.timestamp.isoformat()
            }
        
        return {"device_id": device_id, "message": "No monitoring data"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# PASSWORD RESET ENDPOINTS
# ========================

@app.post("/auth/forgot-password", response_model=dict)
def forgot_password(reset_req: PasswordReset, db: Session = Depends(get_db)):
    """Request password reset"""
    try:
        user = db.query(UserDB).filter(UserDB.email == reset_req.email).first()
        if not user:
            # Don't reveal if email exists (security)
            return {"success": True, "message": "If email exists, reset link will be sent"}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        
        db.commit()
        
        logger.info(f"Password reset token generated for: {reset_req.email}")
        return {
            "success": True,
            "message": "Password reset link sent to email",
            "reset_token": reset_token  # In production, send via email
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/reset-password", response_model=dict)
def reset_password(reset_confirm: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Confirm password reset"""
    try:
        user = db.query(UserDB).filter(
            (UserDB.reset_token == reset_confirm.token) &
            (UserDB.reset_token_expires > datetime.utcnow())
        ).first()
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Update password
        from auth.password import hash_password
        user.password = hash_password(reset_confirm.new_password)
        user.reset_token = None
        user.reset_token_expires = None
        
        db.commit()
        
        logger.info(f"Password reset successful for: {user.email}")
        return {"success": True, "message": "Password reset successful"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# DASHBOARD ENDPOINT
# ========================

@app.get("/dashboard", response_model=dict)
def get_dashboard(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get complete dashboard data"""
    try:
        org_id = current_user.get("org_id")
        
        emp_count = db.query(EmployeeDB).filter(EmployeeDB.org_id == org_id).count()
        dev_count = db.query(DeviceDB).filter(DeviceDB.org_id == org_id).count()
        threat_count = db.query(ThreatDB).filter(ThreatDB.org_id == org_id).count()
        incident_count = db.query(IncidentDB).filter(IncidentDB.org_id == org_id).count()
        
        return {
            "summary": {
                "total_employees": emp_count,
                "total_devices": dev_count,
                "total_threats": threat_count,
                "total_incidents": incident_count
            },
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

logger.info("All endpoints registered successfully")
