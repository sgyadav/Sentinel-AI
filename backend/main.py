"""
SENTINEL AI - COMPLETE BACKEND WITH REAL-TIME MONITORING
Fixed: Unified models, proper device_id handling, process persistence, USB fixes
"""

from models import (
    # SQLAlchemy Models
    Base, UserDB, EmployeeDB, DeviceDB, AssignmentDB, ThreatDB, ProcessDB,
    USBEventDB, SettingsDB, NotificationDB, OrganizationDB,
    LoginHistoryDB, EndpointSessionDB, AuditLogDB,
    # Pydantic Models
    LoginRequest, EmployeeCreate, EmployeeResponse, DeviceCreate, DeviceResponse,
    AssignmentCreate, AssignmentUpdate, AssignmentResponse, ProcessInfo, ProcessList,
    Heartbeat, ThreatResponse, SettingsUpdate, SendEmailRequest, SecurityEvent,
    EndpointSessionEvent
)

import logging
import asyncio
import csv
import io
import json
import os
import re
import sqlite3
from datetime import datetime, timedelta, time as dt_time, timezone
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status, Query, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text, or_, func
from sqlalchemy.orm import sessionmaker, Session
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ============= LOGGING =============
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= DATABASE SETUP =============
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "sentinel.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

HEARTBEAT_ONLINE_SECONDS = 30
DEFAULT_ORG_ID = "default"
LOCAL_TZ = timezone(timedelta(hours=5, minutes=30), "IST")


def get_db():
    """Get database session"""
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


# ============= UTILITIES =============
def hash_password(password: str) -> str:
    return "sha256:" + hashlib.sha256(password.encode()).hexdigest()


def parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        try:
            return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return None


def iso_utc(value):
    timestamp = parse_datetime(value)
    if not timestamp:
        return None
    return timestamp.isoformat() + "Z"


def local_day_bounds_utc(day):
    start_local = datetime.combine(day, dt_time.min, tzinfo=LOCAL_TZ)
    end_local = datetime.combine(day, dt_time.max, tzinfo=LOCAL_TZ)
    return (
        start_local.astimezone(timezone.utc).replace(tzinfo=None),
        end_local.astimezone(timezone.utc).replace(tzinfo=None),
    )


def local_date_filter(period, start_date=None, end_date=None, days=1):
    now_utc = datetime.utcnow()
    today_local = datetime.now(LOCAL_TZ).date()
    start = None
    end = None

    if period == "today":
        start, end = local_day_bounds_utc(today_local)
    elif period == "yesterday":
        start, end = local_day_bounds_utc(today_local - timedelta(days=1))
    elif period in {"last7", "last_7_days"}:
        start = now_utc - timedelta(days=7)
    elif period == "last_month":
        start = now_utc - timedelta(days=30)
    elif period == "custom":
        if start_date:
            start_value = parse_datetime(start_date)
            if len(str(start_date)) == 10:
                start_value = datetime.strptime(str(start_date), "%Y-%m-%d")
            if start_value:
                start, _ = local_day_bounds_utc(start_value.date())
        if end_date:
            end_value = parse_datetime(end_date)
            if len(str(end_date)) == 10:
                end_value = datetime.strptime(str(end_date), "%Y-%m-%d")
            if end_value:
                _, end = local_day_bounds_utc(end_value.date())
    elif period != "all" and days:
        start = now_utc - timedelta(days=days)

    return start, end


def normalize_agent_id(value: str) -> str:
    """Normalize agent IDs to AGT-00001 style when possible."""
    value = (value or "").strip()
    if not value or value.upper() in {"GENERATE_NEW", "UNKNOWN", "NONE", "NULL"}:
        return ""
    match = re.fullmatch(r"AGT[-_ ]?(\d+)", value, flags=re.IGNORECASE)
    if match:
        return f"AGT-{int(match.group(1)):05d}"
    return value


def generate_next_agent_id(db: Session) -> str:
    """Generate the next AGT-xxxxx ID from the devices table."""
    rows = db.query(DeviceDB.device_id).all()
    max_number = 0
    for (device_id,) in rows:
        match = re.fullmatch(r"AGT-(\d{5,})", str(device_id or ""))
        if match:
            max_number = max(max_number, int(match.group(1)))
    return f"AGT-{max_number + 1:05d}"


def generate_device_id(hostname: str, db: Session = None) -> str:
    """Generate a production agent ID. Hostname is kept only for backwards compatibility."""
    if db is not None:
        return generate_next_agent_id(db)
    return f"AGT-{int(datetime.utcnow().timestamp()) % 100000:05d}"


def is_online(last_heartbeat) -> bool:
    age = heartbeat_age_seconds(last_heartbeat)
    return age is not None and age <= HEARTBEAT_ONLINE_SECONDS


def heartbeat_age_seconds(last_heartbeat):
    timestamp = parse_datetime(last_heartbeat)
    if not timestamp:
        return None
    return max(0, int((datetime.utcnow() - timestamp).total_seconds()))


def resolved_status(device: DeviceDB) -> str:
    return "Online" if is_online(device.last_heartbeat) else "Offline"


def update_endpoint_statuses(db: Session):
    """Compatibility hook.

    Endpoint Online/Offline is calculated from last_heartbeat at response time.
    We intentionally do not persist Offline here because a read request should
    not make a currently-heartbeating endpoint look stale in another view.
    """
    return


SAFE_PROCESSES = {
    "chrome.exe", "msedge.exe", "firefox.exe", "explorer.exe", "svchost.exe",
    "winlogon.exe", "csrss.exe", "services.exe", "lsass.exe", "dwm.exe",
    "notepad.exe", "teams.exe", "outlook.exe", "word.exe", "excel.exe",
    "powerpnt.exe", "onedrive.exe", "sentinelagent.exe", "python.exe"
}

SUSPICIOUS_PROCESSES = {
    "powershell.exe", "pwsh.exe", "cmd.exe", "wscript.exe", "cscript.exe",
    "regsvr32.exe", "rundll32.exe", "mshta.exe", "bitsadmin.exe", "certutil.exe",
    "wmic.exe", "psexec.exe", "procdump.exe", "netcat.exe", "nc.exe"
}

CRITICAL_PROCESSES = {
    "mimikatz.exe", "rubeus.exe", "lsassdump.exe", "lazagne.exe", "nanodump.exe",
    "wannacry.exe", "lockbit.exe", "cobaltstrike.exe", "beacon.exe",
    "meterpreter.exe", "bloodhound.exe", "sharphound.exe"
}


def classify_process(name: str):
    normalized = (name or "").lower().strip()
    if normalized in CRITICAL_PROCESSES or any(token in normalized for token in ["mimikatz", "ransom", "meterpreter"]):
        return "Critical", 95, "Known offensive or malware process name"
    if normalized in SUSPICIOUS_PROCESSES:
        return "Suspicious", 55, "Administrative interpreter or dual-use Windows utility"
    if normalized in SAFE_PROCESSES:
        return "Safe", 5, "Common signed operating system or business application"
    return "Safe", 10, "No known suspicious indicator"


def make_threat_id(prefix: str = "THR") -> str:
    return f"{prefix}-{int(datetime.utcnow().timestamp() * 1000)}"


def ensure_threat_for_process(db: Session, device_id: str, process_name: str, classification: str, reason: str):
    if classification not in {"Suspicious", "Critical"}:
        return None

    severity = "Critical" if classification == "Critical" else "Medium"
    existing = db.query(ThreatDB).filter(
        ThreatDB.device_id == device_id,
        ThreatDB.threat_name == process_name,
        ThreatDB.status.in_(["Detected", "Alerted"])
    ).first()
    if existing:
        return existing

    threat = ThreatDB(
        org_id=DEFAULT_ORG_ID,
        threat_id=make_threat_id("PROC"),
        device_id=device_id,
        threat_name=process_name,
        threat_type="Process",
        severity=severity,
        confidence=85 if classification == "Critical" else 60,
        risk_score=95 if classification == "Critical" else 55,
        detection_method="Process classification",
        status="Detected",
        action_taken=reason
    )
    db.add(threat)
    queue_notification(
        db,
        f"{severity} Process Detected",
        f"{process_name} classified as {classification} on {device_id}. {reason}"
    )
    return threat


def queue_notification(db: Session, subject: str, message: str, status_value: str = "Pending"):
    settings = {s.setting_key: s.setting_value for s in db.query(SettingsDB).all()}
    recipient = settings.get("admin_email") or settings.get("smtp_email") or "admin@sentinelai.local"
    notification = NotificationDB(
        notification_id=f"notif_{int(datetime.utcnow().timestamp() * 1000)}",
        recipient_email=recipient,
        subject=subject[:255],
        message=message,
        status=status_value
    )
    db.add(notification)
    return notification


def log_audit(db: Session, action: str, resource_type: str = "", resource_id: str = "", details: dict = None, actor: str = "system"):
    db.add(AuditLogDB(
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id or ""),
        details=json.dumps(details or {})
    ))


class RealtimeHub:
    def __init__(self):
        self.clients = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.clients.discard(websocket)

    async def broadcast(self, message: dict):
        stale = []
        for client in list(self.clients):
            try:
                await client.send_json(message)
            except Exception:
                stale.append(client)
        for client in stale:
            self.disconnect(client)


realtime_hub = RealtimeHub()


def publish_realtime(event_type: str, payload: dict):
    message = {
        "type": event_type,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(realtime_hub.broadcast(message))
    except RuntimeError:
        pass


def ensure_schema():
    """Apply additive SQLite migrations for older local databases."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = conn.cursor()
        table_columns = {}
        for (table_name,) in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            table_columns[table_name] = {row[1] for row in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()}

        def add_column(table, column, definition):
            if table in table_columns and column not in table_columns[table]:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                table_columns[table].add(column)

        add_column("devices", "device_id", "TEXT")
        add_column("devices", "device_type", "TEXT DEFAULT 'Laptop'")
        add_column("devices", "os_version", "TEXT DEFAULT ''")
        add_column("processes", "agent_id", "TEXT DEFAULT ''")
        add_column("processes", "classification", "TEXT DEFAULT 'Safe'")
        add_column("processes", "risk_score", "REAL DEFAULT 0")
        add_column("processes", "reason", "TEXT DEFAULT ''")
        add_column("usb_events", "agent_id", "TEXT DEFAULT ''")
        add_column("threats", "org_id", "TEXT DEFAULT 'default'")
        add_column("threats", "confidence", "REAL DEFAULT 0")
        add_column("threats", "detection_method", "TEXT DEFAULT ''")
        add_column("threats", "file_path", "TEXT DEFAULT ''")
        add_column("threats", "file_hash", "TEXT DEFAULT ''")
        add_column("threats", "action_taken", "TEXT DEFAULT ''")
        add_column("threats", "resolved_at", "DATETIME")
        add_column("threats", "created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS endpoint_sessions (
                id INTEGER PRIMARY KEY,
                agent_id VARCHAR(255) NOT NULL,
                hostname VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL,
                ip_address VARCHAR(45) DEFAULT '',
                login_time DATETIME NOT NULL,
                logout_time DATETIME,
                session_duration INTEGER,
                status VARCHAR(50) DEFAULT 'Active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY,
                actor VARCHAR(255) DEFAULT 'system',
                action VARCHAR(255) NOT NULL,
                resource_type VARCHAR(100) DEFAULT '',
                resource_id VARCHAR(255) DEFAULT '',
                details TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("UPDATE devices SET device_type = COALESCE(device_type, 'Laptop')")
        cursor.execute("UPDATE devices SET os_version = COALESCE(os_version, '')")
        cursor.execute("UPDATE devices SET device_id = 'AGT-' || printf('%05d', id) WHERE device_id IS NULL OR TRIM(device_id) = ''")
        if "processes" in table_columns:
            cursor.execute("DELETE FROM processes WHERE name IS NULL OR TRIM(name) = ''")
        conn.commit()
    finally:
        conn.close()


# ============= STARTUP =============
@app.on_event("startup")
def startup():
    """Initialize database and create admin user"""
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    logger.info("Database initialized")

    db = SessionLocal()
    try:
        # Create admin user if not exists
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
            logger.info("Admin user created: username=admin, password=Admin1234")
        update_endpoint_statuses(db)
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        db.rollback()
    finally:
        db.close()


# ============= HEALTH CHECK =============
@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ============= AUTH ENDPOINTS =============
@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    username = (request.username or "").strip()
    password = request.password or ""
    logger.info(f"Login attempt for user: {username}")
    user = db.query(UserDB).filter(UserDB.username == username).first()

    if not user:
        logger.error(f"User not found: {username}")
        db.add(LoginHistoryDB(
            username=username,
            ip_address="0.0.0.0",
            status="Failed",
            reason="User not found"
        ))
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    hashed_input = hash_password(password)
    stored_password = user.password or ""

    if stored_password != hashed_input:
        if stored_password == password:
            user.password = hashed_input
            logger.info(f"Upgraded legacy password storage for user: {username}")
        else:
            logger.error(f"Password mismatch for user: {username}")
            db.add(LoginHistoryDB(
                username=username,
                ip_address="0.0.0.0",
                status="Failed",
                reason="Invalid password"
            ))
            db.commit()
            raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        logger.error(f"Inactive user login blocked: {username}")
        db.add(LoginHistoryDB(
            username=username,
            ip_address="0.0.0.0",
            status="Failed",
            reason="Inactive user"
        ))
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db.add(LoginHistoryDB(
        username=user.username,
        ip_address="0.0.0.0",
        status="Success",
        reason="Admin login"
    ))
    log_audit(db, "Admin Login", "user", user.username, actor=user.username)
    db.commit()
    publish_realtime("audit", {"action": "Admin Login", "username": user.username})
    logger.info(f"User {username} logged in successfully")
    return {
        "success": True,
        "access_token": f"token_{user.username}_{int(datetime.now().timestamp())}",
        "user": {"username": user.username, "role": user.role, "email": user.email}
    }


@app.post("/auth/logout")
def logout(username: str = Body("admin", embed=True), db: Session = Depends(get_db)):
    last_login = db.query(LoginHistoryDB).filter(
        LoginHistoryDB.username == username,
        LoginHistoryDB.status == "Success",
        LoginHistoryDB.logout_time == None
    ).order_by(LoginHistoryDB.login_time.desc()).first()
    if last_login:
        now = datetime.utcnow()
        last_login.logout_time = now
        login_time = parse_datetime(last_login.login_time) or now
        last_login.session_duration = int((now - login_time).total_seconds())
    log_audit(db, "Admin Logout", "user", username, actor=username)
    db.commit()
    publish_realtime("audit", {"action": "Admin Logout", "username": username})
    return {"success": True, "message": "Logged out"}


# ============= EMPLOYEE ENDPOINTS =============
@app.post("/employees")
def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    try:
        existing = db.query(EmployeeDB).filter(EmployeeDB.employee_id == emp.employee_id).first()
        if existing:
            for key, value in emp.dict().items():
                setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            log_audit(db, "Employee Updated", "employee", emp.employee_id, emp.dict())
            db.commit()
            return {"success": True, "employee_id": emp.employee_id, "message": "Employee updated"}
        new_emp = EmployeeDB(**emp.dict())
        db.add(new_emp)
        log_audit(db, "Employee Added", "employee", emp.employee_id, emp.dict())
        db.commit()
        logger.info(f"Employee created: {emp.employee_id}")
        return {"success": True, "employee_id": emp.employee_id}
    except Exception as e:
        db.rollback()
        logger.error(f"Employee creation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/employees")
def get_employees(db: Session = Depends(get_db)):
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
def update_employee(employee_id: str, emp: EmployeeCreate, db: Session = Depends(get_db)):
    employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    for key, value in emp.dict().items():
        if key != "employee_id":
            setattr(employee, key, value)

    employee.updated_at = datetime.utcnow()
    log_audit(db, "Employee Updated", "employee", employee_id, emp.dict())
    db.commit()
    logger.info(f"Employee updated: {employee_id}")
    return {"success": True, "message": "Employee updated"}


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    log_audit(db, "Employee Deleted", "employee", employee_id)
    db.commit()
    logger.info(f"Employee deleted: {employee_id}")
    return {"success": True, "message": "Employee deleted"}


# ============= DEVICE ENDPOINTS =============
@app.post("/devices")
def create_device(dev: DeviceCreate, db: Session = Depends(get_db)):
    try:
        requested_id = normalize_agent_id(dev.device_id)
        query = db.query(DeviceDB)
        device = None
        if requested_id:
            device = query.filter(DeviceDB.device_id == requested_id).first()
        if not device and dev.mac_address:
            device = query.filter(DeviceDB.mac_address == dev.mac_address).first()
        if not device:
            device = query.filter(DeviceDB.hostname == dev.hostname).first()

        if device:
            device.hostname = dev.hostname
            device.ip_address = dev.ip_address
            device.mac_address = dev.mac_address or device.mac_address
            device.operating_system = dev.operating_system
            device.os_version = dev.os_version
            device.device_type = dev.device_type
            device.updated_at = datetime.utcnow()
            if requested_id and not device.device_id.startswith("AGT-"):
                old_id = device.device_id
                device.device_id = requested_id
                db.query(AssignmentDB).filter(AssignmentDB.device_id == old_id).update({"device_id": requested_id})
            log_audit(db, "Endpoint Updated", "endpoint", device.device_id, dev.dict())
            db.commit()
            logger.info(f"Device updated by create call: {device.device_id}")
            return {"success": True, "device_id": device.device_id, "message": "Endpoint updated"}

        device_id = requested_id or generate_device_id(dev.hostname, db)
        new_dev = DeviceDB(
            device_id=device_id,
            hostname=dev.hostname,
            ip_address=dev.ip_address,
            mac_address=dev.mac_address,
            operating_system=dev.operating_system,
            os_version=dev.os_version,
            device_type=dev.device_type,
            status="Offline"
        )
        db.add(new_dev)
        log_audit(db, "Endpoint Added", "endpoint", device_id, dev.dict())
        db.commit()
        logger.info(f"Device created: {device_id}")
        return {"success": True, "device_id": device_id}
    except Exception as e:
        db.rollback()
        logger.error(f"Device creation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/devices")
def get_devices(
    search: str = Query("", description="Search hostname, employee, department, IP, or agent ID"),
    db: Session = Depends(get_db)
):
    update_endpoint_statuses(db)
    devices = db.query(DeviceDB).all()
    assignments = db.query(AssignmentDB).filter(AssignmentDB.is_active == True).all()
    employees = {e.employee_id: e for e in db.query(EmployeeDB).all()}
    employee_by_device = {}
    for assignment in assignments:
        employee_by_device[assignment.device_id] = employees.get(assignment.employee_id)

    if search:
        needle = search.lower()
        filtered = []
        for d in devices:
            employee = employee_by_device.get(d.device_id)
            haystack = " ".join([
                d.device_id or "",
                d.hostname or "",
                d.ip_address or "",
                d.mac_address or "",
                employee.name if employee else "",
                employee.employee_id if employee else "",
                employee.department if employee else "",
            ]).lower()
            if needle in haystack:
                filtered.append(d)
        devices = filtered

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
                "status": resolved_status(d),
                "computed_status": resolved_status(d),
                "last_heartbeat": d.last_heartbeat.isoformat() if d.last_heartbeat else None,
                "heartbeat_age_seconds": heartbeat_age_seconds(d.last_heartbeat),
                "heartbeat_timeout_seconds": HEARTBEAT_ONLINE_SECONDS,
                "employee": (
                    {
                        "employee_id": employee_by_device[d.device_id].employee_id,
                        "name": employee_by_device[d.device_id].name,
                        "department": employee_by_device[d.device_id].department
                    }
                    if employee_by_device.get(d.device_id) else None
                )
            }
            for d in devices
        ]
    }


@app.put("/devices/{device_id}")
def update_device(device_id: str, dev: DeviceCreate, db: Session = Depends(get_db)):
    device = db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.hostname = dev.hostname
    device.ip_address = dev.ip_address
    device.mac_address = dev.mac_address
    device.operating_system = dev.operating_system
    device.os_version = dev.os_version
    device.device_type = dev.device_type
    device.updated_at = datetime.utcnow()

    log_audit(db, "Endpoint Updated", "endpoint", device_id, dev.dict())
    db.commit()
    logger.info(f"Device updated: {device_id}")
    return {"success": True, "message": "Device updated"}


@app.delete("/devices/{device_id}")
def delete_device(device_id: str, db: Session = Depends(get_db)):
    device = db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    db.delete(device)
    log_audit(db, "Endpoint Deleted", "endpoint", device_id)
    db.commit()
    logger.info(f"Device deleted: {device_id}")
    return {"success": True, "message": "Device deleted"}


# ============= ASSIGNMENT ENDPOINTS =============
@app.post("/assignments")
def create_assignment(assign: AssignmentCreate, db: Session = Depends(get_db)):
    try:
        employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == assign.employee_id).first()
        device = db.query(DeviceDB).filter(DeviceDB.device_id == assign.device_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        if not device:
            raise HTTPException(status_code=404, detail="Endpoint not found")

        db.query(AssignmentDB).filter(
            AssignmentDB.device_id == assign.device_id,
            AssignmentDB.is_active == True
        ).update({"is_active": False})
        db.query(AssignmentDB).filter(
            AssignmentDB.employee_id == assign.employee_id,
            AssignmentDB.device_id == assign.device_id
        ).delete()
        new_assign = AssignmentDB(**assign.dict())
        db.add(new_assign)
        log_audit(db, "Device Assigned", "assignment", assign.device_id, assign.dict())
        db.commit()
        logger.info(f"Assignment created: {assign.employee_id} -> {assign.device_id}")
        return {"success": True, "message": "Device assigned"}
    except Exception as e:
        db.rollback()
        logger.error(f"Assignment error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/assignments")
def get_assignments(db: Session = Depends(get_db)):
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
    db: Session = Depends(get_db)
):
    existing = db.query(AssignmentDB).filter(AssignmentDB.id == assignment_id).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Assignment not found")

    existing.employee_id = assignment.employee_id
    existing.device_id = assignment.device_id
    db.query(AssignmentDB).filter(
        AssignmentDB.device_id == assignment.device_id,
        AssignmentDB.id != assignment_id,
        AssignmentDB.is_active == True
    ).update({"is_active": False})
    log_audit(db, "Assignment Updated", "assignment", assignment_id, assignment.dict())
    db.commit()
    logger.info(f"Assignment updated: {assignment_id}")
    return {"success": True, "message": "Assignment updated successfully"}


@app.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(AssignmentDB).filter(AssignmentDB.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(assignment)
    log_audit(db, "Assignment Deleted", "assignment", assignment_id)
    db.commit()
    logger.info(f"Assignment deleted: {assignment_id}")
    return {"success": True, "message": "Assignment deleted successfully"}


# ============= THREAT ENDPOINTS =============
@app.get("/threats")
def get_threats(db: Session = Depends(get_db)):
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


@app.delete("/threats/clear")
def clear_threats(admin: str = Query("admin"), db: Session = Depends(get_db)):
    try:
        count = db.query(ThreatDB).count()
        db.query(ThreatDB).delete()
        log_audit(db, "Threats Cleared", "threat", "all", {"cleared_count": count}, actor=admin)
        db.commit()
        publish_realtime("threats_cleared", {"cleared_count": count, "admin": admin})
        return {"success": True, "message": f"{count} threat(s) cleared", "cleared_count": count}
    except Exception as e:
        db.rollback()
        logger.error(f"Clear threats error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============= HEARTBEAT ENDPOINT =============
@app.post("/heartbeat")
def heartbeat(data: Heartbeat, db: Session = Depends(get_db)):
    try:
        incoming_agent_id = normalize_agent_id(data.agent_id or data.device_uuid)
        device = None

        if incoming_agent_id and incoming_agent_id.startswith("AGT-"):
            device = db.query(DeviceDB).filter(DeviceDB.device_id == incoming_agent_id).first()
        if not device and data.mac_address:
            device = db.query(DeviceDB).filter(DeviceDB.mac_address == data.mac_address).first()
        if not device:
            device = db.query(DeviceDB).filter(DeviceDB.hostname == data.hostname).first()

        is_new = False
        if not device:
            incoming_agent_id = incoming_agent_id if incoming_agent_id.startswith("AGT-") else ""
            device = DeviceDB(
                device_id=incoming_agent_id or generate_next_agent_id(db),
                hostname=data.hostname,
                ip_address=data.ip_address,
                mac_address=data.mac_address,
                operating_system=data.operating_system,
                os_version=data.os_version,
                device_type=data.device_type or "Laptop",
                status="Online",
                last_heartbeat=datetime.utcnow()
            )
            db.add(device)
            is_new = True
        else:
            if not str(device.device_id or "").startswith("AGT-"):
                old_id = device.device_id
                device.device_id = incoming_agent_id if incoming_agent_id.startswith("AGT-") else generate_next_agent_id(db)
                db.query(AssignmentDB).filter(AssignmentDB.device_id == old_id).update({"device_id": device.device_id})

        device.hostname = data.hostname
        device.ip_address = data.ip_address
        device.mac_address = data.mac_address or device.mac_address
        device.operating_system = data.operating_system
        device.os_version = data.os_version or device.os_version
        device.device_type = data.device_type or device.device_type or "Laptop"
        device.cpu_usage = data.cpu_usage
        device.ram_usage = data.ram_usage
        device.disk_usage = data.disk_usage
        device.status = "Online"
        device.last_heartbeat = datetime.utcnow()
        device.updated_at = datetime.utcnow()

        log_audit(
            db,
            "Endpoint Registered" if is_new else "Heartbeat Received",
            "endpoint",
            device.device_id,
            {"hostname": data.hostname, "username": data.username}
        )
        db.commit()
        publish_realtime("heartbeat", {
            "device_id": device.device_id,
            "hostname": device.hostname,
            "status": "Online",
            "cpu_usage": device.cpu_usage,
            "ram_usage": device.ram_usage,
            "disk_usage": device.disk_usage,
            "last_heartbeat": device.last_heartbeat.isoformat(),
            "heartbeat_age_seconds": 0,
            "heartbeat_timeout_seconds": HEARTBEAT_ONLINE_SECONDS
        })
        logger.info(f"Heartbeat upserted: {device.device_id} {data.hostname}")
        return {
            "success": True,
            "message": "New Device Registered" if is_new else "Heartbeat Updated",
            "device_id": device.device_id,
            "agent_id": device.device_id,
            "last_heartbeat": device.last_heartbeat.isoformat(),
            "heartbeat_age_seconds": 0,
            "heartbeat_window_seconds": HEARTBEAT_ONLINE_SECONDS
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Heartbeat error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============= PROCESS ENDPOINTS =============
@app.post("/processes")
def receive_processes(payload=Body(...), db: Session = Depends(get_db)):
    try:
        if isinstance(payload, dict):
            processes = payload.get("processes", [])
            hostname = payload.get("hostname") or "Unknown"
            agent_id = normalize_agent_id(payload.get("agent_id") or payload.get("device_id") or "")
        else:
            processes = payload if isinstance(payload, list) else []
            first = processes[0] if processes and isinstance(processes[0], dict) else {}
            hostname = first.get("hostname") or "Unknown"
            agent_id = normalize_agent_id(first.get("agent_id") or first.get("device_id") or "")

        device = None
        if agent_id:
            device = db.query(DeviceDB).filter(DeviceDB.device_id == agent_id).first()
        if not device and hostname != "Unknown":
            device = db.query(DeviceDB).filter(DeviceDB.hostname == hostname).first()
        if device:
            agent_id = device.device_id
            hostname = device.hostname

        # Clear old snapshot for this endpoint. This keeps the SOC view live instead of accumulating stale rows.
        if agent_id:
            db.query(ProcessDB).filter(ProcessDB.agent_id == agent_id).delete()
        else:
            db.query(ProcessDB).filter(ProcessDB.hostname == hostname).delete()

        stored = 0
        for proc in processes:
            if isinstance(proc, dict):
                name = proc.get("name") or proc.get("process_name") or proc.get("ProcessName") or ""
                username = proc.get("username") or proc.get("user") or proc.get("User") or "Unknown"
                cpu_value = proc.get("cpu_percent", proc.get("cpu", proc.get("CPU", 0)))
                memory_value = proc.get("memory_percent", proc.get("memory", proc.get("Memory", 0)))
                classification, risk_score, reason = classify_process(name)
                process_db = ProcessDB(
                    agent_id=agent_id,
                    hostname=proc.get("hostname") or hostname,
                    pid=proc.get("pid", 0),
                    name=name,
                    cpu_percent=float(cpu_value or 0),
                    memory_percent=float(memory_value or 0),
                    username=username,
                    classification=classification,
                    risk_score=risk_score,
                    reason=reason,
                    updated_at=datetime.utcnow()
                )
                db.add(process_db)
                stored += 1
                if device:
                    ensure_threat_for_process(db, device.device_id, name, classification, reason)

        db.commit()
        publish_realtime("processes", {"agent_id": agent_id, "hostname": hostname, "count": stored})
        logger.info(f"Received {stored} processes from {hostname}")
        return {"success": True, "message": f"{stored} processes received", "agent_id": agent_id, "hostname": hostname}

    except Exception as e:
        db.rollback()
        logger.error(f"Process error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/processes/live")
def get_live_processes(
    hostname: str = None,
    agent_id: str = None,
    classification: str = None,
    limit: int = Query(500, ge=1, le=2000),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(ProcessDB)
        normalized_agent_id = normalize_agent_id(agent_id or "")
        if normalized_agent_id:
            query = query.filter(ProcessDB.agent_id == normalized_agent_id)
        if hostname:
            query = query.filter(ProcessDB.hostname == hostname)
        if classification:
            query = query.filter(ProcessDB.classification == classification)

        query = query.filter(ProcessDB.name != "")
        processes = query.order_by(ProcessDB.risk_score.desc(), ProcessDB.cpu_percent.desc(), ProcessDB.memory_percent.desc()).limit(limit).all()

        return {
            "total": len(processes),
            "processes": [
                {
                    "agent_id": p.agent_id,
                    "pid": p.pid,
                    "name": p.name,
                    "process_name": p.name,
                    "cpu_percent": p.cpu_percent,
                    "memory_percent": p.memory_percent,
                    "username": p.username,
                    "user": p.username,
                    "hostname": p.hostname,
                    "classification": p.classification,
                    "risk_score": p.risk_score,
                    "reason": p.reason
                }
                for p in processes
            ]
        }
    except Exception as e:
        logger.error(f"Get processes error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/processes/clear")
def clear_processes(admin: str = Query("admin"), db: Session = Depends(get_db)):
    try:
        count = db.query(ProcessDB).count()
        db.query(ProcessDB).delete()
        log_audit(db, "Processes Cleared", "process", "all", {"cleared_count": count}, actor=admin)
        db.commit()
        publish_realtime("processes_cleared", {"cleared_count": count, "admin": admin})
        return {"success": True, "message": f"{count} process row(s) cleared", "cleared_count": count}
    except Exception as e:
        db.rollback()
        logger.error(f"Clear processes error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============= USB EVENTS ENDPOINTS =============
@app.post("/usb-events")
def receive_usb_event(event: dict, db: Session = Depends(get_db)):
    try:
        usb = USBEventDB(
            agent_id=normalize_agent_id(event.get("agent_id") or event.get("device_id") or ""),
            action=event.get("action", "Unknown"),
            device=event.get("device", "Unknown"),
            hostname=event.get("hostname", "Unknown"),
            username=event.get("username", "Unknown"),
            event_time=parse_datetime(event.get("event_time")) or datetime.utcnow()
        )
        db.add(usb)
        if usb.action.lower() == "inserted":
            queue_notification(
                db,
                f"USB Inserted on {usb.hostname}",
                f"USB device {usb.device} inserted by {usb.username} on {usb.hostname}."
            )
        log_audit(db, "USB Event", "usb", usb.device, {
            "action": usb.action,
            "hostname": usb.hostname,
            "username": usb.username
        })
        db.commit()
        publish_realtime("usb", {
            "agent_id": usb.agent_id,
            "action": usb.action,
            "device": usb.device,
            "hostname": usb.hostname,
            "username": usb.username,
            "event_time": usb.event_time.isoformat()
        })

        logger.info(f"USB Event: {event.get('action')} on {event.get('device')} from {event.get('hostname')}")
        return {"success": True, "message": "USB Event Stored Successfully"}

    except Exception as e:
        db.rollback()
        logger.error(f"USB event error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/usb-events")
def get_usb_events(
    period: str = Query("today", description="today, yesterday, last7, last_month, custom, all"),
    days: int = 1,
    start_date: str = None,
    end_date: str = None,
    search: str = "",
    db: Session = Depends(get_db)
):
    try:
        start, end = local_date_filter(period, start_date, end_date, days)

        query = db.query(USBEventDB)
        if start:
            query = query.filter(USBEventDB.event_time >= start)
        if end:
            query = query.filter(USBEventDB.event_time <= end)
        if search:
            needle = f"%{search.lower()}%"
            query = query.filter(or_(
                func.lower(USBEventDB.device).like(needle),
                func.lower(USBEventDB.hostname).like(needle),
                func.lower(USBEventDB.username).like(needle),
                func.lower(USBEventDB.agent_id).like(needle),
            ))

        events = query.order_by(
            USBEventDB.event_time.desc()
        ).all()

        return {
            "total": len(events),
            "events": [
                {
                    "id": e.id,
                    "agent_id": e.agent_id,
                    "action": e.action,
                    "device": e.device,
                    "hostname": e.hostname,
                    "username": e.username,
                    "event_time": iso_utc(e.event_time)
                }
                for e in events
            ]
        }
    except Exception as e:
        logger.error(f"Get USB events error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/usb-events/clear")
def clear_usb_events(admin: str = Query("admin"), db: Session = Depends(get_db)):
    try:
        count = db.query(USBEventDB).count()
        db.query(USBEventDB).delete()
        log_audit(db, "USB Events Cleared", "usb", "all", {"cleared_count": count}, actor=admin)
        db.commit()
        publish_realtime("usb_events_cleared", {"cleared_count": count, "admin": admin})
        return {"success": True, "message": f"{count} USB event(s) cleared", "cleared_count": count}
    except Exception as e:
        db.rollback()
        logger.error(f"Clear USB events error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============= DASHBOARD ENDPOINT =============
@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    try:
        update_endpoint_statuses(db)
        emp_count = db.query(EmployeeDB).count()
        devices = db.query(DeviceDB).all()
        dev_count = len(devices)
        threat_count = db.query(ThreatDB).count()
        online_count = sum(1 for d in devices if resolved_status(d) == "Online")
        offline_count = dev_count - online_count
        today_start = datetime.combine(datetime.utcnow().date(), dt_time.min)
        usb_today = db.query(USBEventDB).filter(USBEventDB.event_time >= today_start).count()
        process_count = db.query(ProcessDB).count()
        avg_cpu = sum(float(d.cpu_usage or 0) for d in devices) / dev_count if dev_count else 0
        avg_ram = sum(float(d.ram_usage or 0) for d in devices) / dev_count if dev_count else 0

        return {
            "summary": {
                "total_employees": emp_count,
                "total_devices": dev_count,
                "total_threats": threat_count,
                "online_devices": online_count,
                "offline_devices": offline_count,
                "total_incidents": threat_count,
                "usb_today": usb_today,
                "process_count": process_count,
                "cpu_average": round(avg_cpu, 2),
                "ram_average": round(avg_ram, 2)
            },
            "status": "operational"
        }
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============= EMPLOYEE MONITORING ENDPOINT =============
@app.get("/employee-monitoring")
def get_employee_monitoring(db: Session = Depends(get_db)):
    try:
        employees = db.query(EmployeeDB).all()
        monitoring_data = []

        for emp in employees:
            assignments = db.query(AssignmentDB).filter(
                AssignmentDB.employee_id == emp.employee_id
            ).all()
            device_count = len(assignments)

            device_ids = [a.device_id for a in assignments]
            threats = db.query(ThreatDB).filter(
                ThreatDB.device_id.in_(device_ids)
            ).all() if device_ids else []
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

    except Exception as e:
        logger.error(f"Employee monitoring error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============= LOGIN / LOGOUT MONITORING =============
@app.post("/endpoint-sessions")
def receive_endpoint_session(event: EndpointSessionEvent, db: Session = Depends(get_db)):
    try:
        agent_id = normalize_agent_id(event.agent_id)
        event_time = parse_datetime(event.event_time) or datetime.utcnow()

        if event.action == "login":
            if agent_id or event.hostname:
                stale_query = db.query(EndpointSessionDB).filter(
                    EndpointSessionDB.logout_time == None,
                    EndpointSessionDB.username != event.username
                )
                if agent_id:
                    stale_query = stale_query.filter(EndpointSessionDB.agent_id == agent_id)
                else:
                    stale_query = stale_query.filter(EndpointSessionDB.hostname == event.hostname)
                for stale in stale_query.all():
                    stale.logout_time = event_time
                    stale.status = "Closed"
                    login_time = parse_datetime(stale.login_time) or event_time
                    stale.session_duration = max(0, int((event_time - login_time).total_seconds()))

            active = db.query(EndpointSessionDB).filter(
                EndpointSessionDB.agent_id == agent_id,
                EndpointSessionDB.username == event.username,
                EndpointSessionDB.logout_time == None
            ).first()
            if not active:
                active = EndpointSessionDB(
                    agent_id=agent_id,
                    hostname=event.hostname,
                    username=event.username,
                    ip_address=event.ip_address,
                    login_time=event_time,
                    status="Active"
                )
                db.add(active)
            log_audit(db, "Windows Login", "endpoint_session", agent_id, {
                "hostname": event.hostname,
                "username": event.username
            })
        else:
            active = db.query(EndpointSessionDB).filter(
                EndpointSessionDB.agent_id == agent_id,
                EndpointSessionDB.username == event.username,
                EndpointSessionDB.logout_time == None
            ).order_by(EndpointSessionDB.login_time.desc()).first()
            if not active:
                if agent_id or event.hostname:
                    fallback = db.query(EndpointSessionDB).filter(
                        EndpointSessionDB.logout_time == None
                    )
                    if agent_id:
                        fallback = fallback.filter(EndpointSessionDB.agent_id == agent_id)
                    else:
                        fallback = fallback.filter(EndpointSessionDB.hostname == event.hostname)
                    active = fallback.order_by(EndpointSessionDB.login_time.desc()).first()
            if active:
                active.logout_time = event_time
                active.status = "Closed"
                login_time = parse_datetime(active.login_time) or event_time
                active.session_duration = max(0, int((event_time - login_time).total_seconds()))
            else:
                active = EndpointSessionDB(
                    agent_id=agent_id,
                    hostname=event.hostname,
                    username=event.username,
                    ip_address=event.ip_address,
                    login_time=event_time,
                    logout_time=event_time,
                    session_duration=0,
                    status="Closed"
                )
                db.add(active)
            log_audit(db, "Windows Logout", "endpoint_session", agent_id, {
                "hostname": event.hostname,
                "username": event.username
            })

        db.commit()
        publish_realtime("endpoint_session", {
            "agent_id": agent_id,
            "hostname": event.hostname,
            "username": event.username,
            "action": event.action,
            "event_time": event_time.isoformat()
        })
        return {"success": True, "message": f"{event.action} recorded"}
    except Exception as e:
        db.rollback()
        logger.error(f"Endpoint session error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/login-events")
def get_login_events(
    agent_id: str = "",
    hostname: str = "",
    username: str = "",
    period: str = Query("today", description="today, yesterday, last7, custom, all"),
    start_date: str = None,
    end_date: str = None,
    search: str = "",
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(EndpointSessionDB)
    start, end = local_date_filter(period, start_date, end_date)
    if start:
        query = query.filter(EndpointSessionDB.login_time >= start)
    if end:
        query = query.filter(EndpointSessionDB.login_time <= end)
    if agent_id:
        query = query.filter(EndpointSessionDB.agent_id == normalize_agent_id(agent_id))
    if hostname:
        query = query.filter(EndpointSessionDB.hostname == hostname)
    if username:
        query = query.filter(EndpointSessionDB.username == username)
    if search:
        needle = f"%{search.lower()}%"
        query = query.filter(or_(
            func.lower(EndpointSessionDB.username).like(needle),
            func.lower(EndpointSessionDB.hostname).like(needle),
            func.lower(EndpointSessionDB.agent_id).like(needle),
        ))
    sessions = query.order_by(EndpointSessionDB.login_time.desc()).limit(limit).all()
    return {
        "total": len(sessions),
        "events": [
            {
                "id": session.id,
                "agent_id": session.agent_id,
                "hostname": session.hostname,
                "username": session.username,
                "ip_address": session.ip_address,
                "login_time": iso_utc(session.login_time),
                "logout_time": iso_utc(session.logout_time),
                "session_duration": session.session_duration,
                "status": session.status,
            }
            for session in sessions
        ]
    }


# ============= ENDPOINT DETAILS / TIMELINE =============
@app.get("/devices/{device_id}/details")
def get_device_details(device_id: str, db: Session = Depends(get_db)):
    update_endpoint_statuses(db)
    device = db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    assignment = db.query(AssignmentDB).filter(
        AssignmentDB.device_id == device_id,
        AssignmentDB.is_active == True
    ).first()
    employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == assignment.employee_id).first() if assignment else None

    return {
        "device": {
            "device_id": device.device_id,
            "hostname": device.hostname,
            "ip_address": device.ip_address,
            "mac_address": device.mac_address,
            "operating_system": device.operating_system,
            "os_version": device.os_version,
            "device_type": device.device_type,
            "cpu_usage": device.cpu_usage,
            "ram_usage": device.ram_usage,
            "disk_usage": device.disk_usage,
            "status": resolved_status(device),
            "last_heartbeat": device.last_heartbeat.isoformat() if device.last_heartbeat else None,
            "heartbeat_age_seconds": heartbeat_age_seconds(device.last_heartbeat),
            "heartbeat_timeout_seconds": HEARTBEAT_ONLINE_SECONDS,
        },
        "employee": {
            "employee_id": employee.employee_id,
            "name": employee.name,
            "department": employee.department,
            "email": employee.email,
        } if employee else None,
        "counts": {
            "usb": db.query(USBEventDB).filter(or_(USBEventDB.agent_id == device_id, USBEventDB.hostname == device.hostname)).count(),
            "processes": db.query(ProcessDB).filter(or_(ProcessDB.agent_id == device_id, ProcessDB.hostname == device.hostname)).count(),
            "threats": db.query(ThreatDB).filter(ThreatDB.device_id == device_id).count(),
            "logins": db.query(EndpointSessionDB).filter(or_(EndpointSessionDB.agent_id == device_id, EndpointSessionDB.hostname == device.hostname)).count(),
        }
    }


@app.get("/devices/{device_id}/timeline")
def get_device_timeline(device_id: str, limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    device = db.query(DeviceDB).filter(DeviceDB.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    events = []
    for session in db.query(EndpointSessionDB).filter(or_(EndpointSessionDB.agent_id == device_id, EndpointSessionDB.hostname == device.hostname)).all():
        events.append({
            "time": session.login_time,
            "type": "Login",
            "title": f"{session.username} logged in",
            "severity": "Info",
        })
        if session.logout_time:
            events.append({
                "time": session.logout_time,
                "type": "Logout",
                "title": f"{session.username} logged out",
                "severity": "Info",
            })
    for event in db.query(USBEventDB).filter(or_(USBEventDB.agent_id == device_id, USBEventDB.hostname == device.hostname)).all():
        events.append({
            "time": event.event_time,
            "type": "USB",
            "title": f"{event.action}: {event.device}",
            "severity": "Medium" if event.action == "Inserted" else "Low",
        })
    for process in db.query(ProcessDB).filter(or_(ProcessDB.agent_id == device_id, ProcessDB.hostname == device.hostname)).filter(ProcessDB.classification != "Safe").all():
        events.append({
            "time": process.updated_at or process.created_at,
            "type": "Process",
            "title": f"{process.name} classified as {process.classification}",
            "severity": "High" if process.classification == "Critical" else "Medium",
        })
    for threat in db.query(ThreatDB).filter(ThreatDB.device_id == device_id).all():
        events.append({
            "time": threat.detected_at,
            "type": "Threat",
            "title": threat.threat_name,
            "severity": threat.severity,
        })

    events = sorted(events, key=lambda item: parse_datetime(item["time"]) or datetime.min, reverse=True)[:limit]
    return {
        "device_id": device_id,
        "hostname": device.hostname,
        "events": [
            {
                **event,
                "time": event["time"].isoformat() if isinstance(event["time"], datetime) else str(event["time"])
            }
            for event in events
        ]
    }


@app.get("/audit-logs")
def get_audit_logs(limit: int = Query(200, ge=1, le=1000), db: Session = Depends(get_db)):
    logs = db.query(AuditLogDB).order_by(AuditLogDB.created_at.desc()).limit(limit).all()
    return {
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "actor": log.actor,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
    }


# ============= REPORTS =============
def report_rows(report_type: str, db: Session):
    report_type = report_type.lower()
    if report_type in {"employee", "employees"}:
        return ["Employee ID", "Name", "Email", "Phone", "Department", "Designation", "Risk Score"], [
            [e.employee_id, e.name, e.email, e.phone, e.department, e.designation, e.risk_score]
            for e in db.query(EmployeeDB).all()
        ]
    if report_type in {"endpoint", "endpoints", "device", "devices"}:
        update_endpoint_statuses(db)
        return ["Agent ID", "Hostname", "IP", "MAC", "OS", "CPU %", "RAM %", "Disk %", "Status", "Last Heartbeat"], [
            [d.device_id, d.hostname, d.ip_address, d.mac_address, d.operating_system, d.cpu_usage, d.ram_usage, d.disk_usage, resolved_status(d), d.last_heartbeat.isoformat() if d.last_heartbeat else ""]
            for d in db.query(DeviceDB).all()
        ]
    if report_type in {"threat", "threats"}:
        return ["Threat ID", "Agent ID", "Name", "Type", "Severity", "Risk Score", "Status", "Detected At"], [
            [t.threat_id, t.device_id, t.threat_name, t.threat_type, t.severity, t.risk_score, t.status, t.detected_at.isoformat() if t.detected_at else ""]
            for t in db.query(ThreatDB).all()
        ]
    if report_type == "usb":
        return ["Agent ID", "Action", "Device", "Hostname", "Username", "Event Time"], [
            [u.agent_id, u.action, u.device, u.hostname, u.username, u.event_time.isoformat() if u.event_time else ""]
            for u in db.query(USBEventDB).order_by(USBEventDB.event_time.desc()).all()
        ]
    if report_type in {"login", "logins"}:
        return ["Agent ID", "Hostname", "Username", "Login Time", "Logout Time", "Duration Seconds", "Status"], [
            [s.agent_id, s.hostname, s.username, s.login_time.isoformat() if s.login_time else "", s.logout_time.isoformat() if s.logout_time else "", s.session_duration or "", s.status]
            for s in db.query(EndpointSessionDB).order_by(EndpointSessionDB.login_time.desc()).all()
        ]
    raise HTTPException(status_code=404, detail="Unknown report type")


@app.get("/reports/{report_type}/csv")
def export_csv_report(report_type: str, db: Session = Depends(get_db)):
    headers, rows = report_rows(report_type, db)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    filename = f"{report_type}_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/reports/{report_type}/pdf")
def export_pdf_report(report_type: str, db: Session = Depends(get_db)):
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(status_code=500, detail="ReportLab is not installed")

    headers, rows = report_rows(report_type, db)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"SENTINEL AI - {report_type.title()} Report", styles["Title"]),
        Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", styles["Normal"]),
        Spacer(1, 12)
    ]
    table_rows = [headers] + [[str(value) for value in row] for row in rows[:200]]
    table = Table(table_rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    filename = f"{report_type}_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ============= SETTINGS ENDPOINTS =============
@app.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    try:
        settings = db.query(SettingsDB).all()
        settings_dict = {s.setting_key: s.setting_value for s in settings}
        return {
            "smtp_server": settings_dict.get("smtp_server", ""),
            "smtp_port": int(settings_dict.get("smtp_port", "587")),
            "smtp_email": settings_dict.get("smtp_email", ""),
            "smtp_password": "*" * min(8, len(settings_dict.get("smtp_password", ""))),
            "admin_email": settings_dict.get("admin_email", "")
        }
    except Exception as e:
        logger.error(f"Settings error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/settings")
def update_settings(settings: SettingsUpdate, db: Session = Depends(get_db)):
    try:
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

        log_audit(db, "Settings Updated", "settings", "email")
        db.commit()
        logger.info("Settings updated")
        return {"success": True, "message": "Settings updated successfully"}

    except Exception as e:
        db.rollback()
        logger.error(f"Settings update error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============= EMAIL ENDPOINTS =============
@app.post("/test-email")
def test_email(request: SendEmailRequest, db: Session = Depends(get_db)):
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

        logger.info(f"Test email sent to {request.to_email}")
        return {"success": True, "message": "Test email sent successfully"}

    except Exception as e:
        logger.error(f"Test email error: {str(e)}")
        return {"success": False, "message": str(e)}


@app.post("/send-email")
def send_email_notification(request: SendEmailRequest, db: Session = Depends(get_db)):
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

        logger.info(f"Email sent to {request.to_email}")
        return {"success": True, "message": "Email sent successfully"}

    except Exception as e:
        db.rollback()
        logger.error(f"Send email error: {str(e)}")
        return {"success": False, "message": str(e)}


@app.get("/notifications")
def get_notifications(db: Session = Depends(get_db)):
    try:
        notifications = db.query(NotificationDB).order_by(
            NotificationDB.created_at.desc()
        ).limit(50).all()

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
    except Exception as e:
        logger.error(f"Notifications error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============= REALTIME WEBSOCKET =============
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await realtime_hub.connect(websocket)
    try:
        await websocket.send_json({
            "type": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "SENTINEL AI realtime monitoring connected"
        })
        while True:
            message = await websocket.receive_text()
            if message.lower() == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
    except WebSocketDisconnect:
        realtime_hub.disconnect(websocket)
    except Exception:
        realtime_hub.disconnect(websocket)


@app.get("/realtime/status")
def realtime_status():
    return {
        "realtime_enabled": True,
        "connected_clients": len(realtime_hub.clients),
        "timestamp": datetime.utcnow().isoformat()
    }


# ============= MAIN =============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
