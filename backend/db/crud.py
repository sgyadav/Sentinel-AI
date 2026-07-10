from sqlalchemy.orm import Session

from .models import (
    UserDB,
    EmployeeDB,
    DeviceDB,
    IncidentDB
)

# ==========================================================
# USER CRUD
# ==========================================================

def create_user(db: Session, user):

    db_user = UserDB(
        username=user.username,
        password=user.password,
        role=user.role,
        organization=user.organization,
        email=user.email
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_username(db: Session, username: str):

    return (
        db.query(UserDB)
        .filter(UserDB.username == username)
        .first()
    )


def get_users(db: Session):

    return db.query(UserDB).all()


# ==========================================================
# EMPLOYEE CRUD
# ==========================================================

def create_employee(db: Session, employee):

    db_employee = EmployeeDB(
        employee_id=employee.employee_id,
        name=employee.name,
        department=employee.department,
        designation=employee.designation,
        email=employee.email,
        risk_score=0
    )

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return db_employee


def get_employees(db: Session):

    return db.query(EmployeeDB).all()


# ==========================================================
# DEVICE CRUD
# ==========================================================

def create_device(db: Session, device):

    db_device = DeviceDB(
        hostname=device.hostname,
        ip_address=device.ip_address,
        operating_system=device.operating_system,
        status="Online"
    )

    db.add(db_device)
    db.commit()
    db.refresh(db_device)

    return db_device


def get_devices(db: Session):

    return db.query(DeviceDB).all()


# ==========================================================
# INCIDENT CRUD
# ==========================================================

def create_incident(db: Session, incident):

    db_incident = IncidentDB(
        incident_id=incident.incident_id,
        hostname=incident.hostname,
        attack_type=incident.attack_type,
        risk_score=incident.risk_score,
        status=incident.status,
        recommendation=incident.recommendation
    )

    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return db_incident


def get_incidents(db: Session):

    return db.query(IncidentDB).all()