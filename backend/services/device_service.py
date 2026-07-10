from sqlalchemy.orm import Session
from sqlalchemy import or_

from db.models import DeviceDB


# =====================================================
# CREATE DEVICE
# =====================================================

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


# =====================================================
# GET ALL DEVICES
# =====================================================

def get_all_devices(db: Session):

    return db.query(DeviceDB).all()


# =====================================================
# GET SINGLE DEVICE
# =====================================================

def get_device(db: Session, hostname: str):

    return (
        db.query(DeviceDB)
        .filter(DeviceDB.hostname == hostname)
        .first()
    )


# =====================================================
# UPDATE DEVICE
# =====================================================

def update_device(
    db: Session,
    hostname: str,
    device
):

    db_device = (
        db.query(DeviceDB)
        .filter(DeviceDB.hostname == hostname)
        .first()
    )

    if not db_device:
        return {
            "success": False,
            "message": "Device Not Found"
        }

    db_device.ip_address = device.ip_address
    db_device.operating_system = device.operating_system
    db_device.status = device.status

    db.commit()
    db.refresh(db_device)

    return db_device


# =====================================================
# DELETE DEVICE
# =====================================================

def delete_device(
    db: Session,
    hostname: str
):

    db_device = (
        db.query(DeviceDB)
        .filter(DeviceDB.hostname == hostname)
        .first()
    )

    if not db_device:
        return {
            "success": False,
            "message": "Device Not Found"
        }

    db.delete(db_device)
    db.commit()

    return {
        "success": True,
        "message": "Device Deleted Successfully"
    }


# =====================================================
# SEARCH DEVICE
# =====================================================

def search_device(
    db: Session,
    keyword: str
):

    return (
        db.query(DeviceDB)
        .filter(
            or_(
                DeviceDB.hostname.contains(keyword),
                DeviceDB.ip_address.contains(keyword),
                DeviceDB.operating_system.contains(keyword),
                DeviceDB.status.contains(keyword)
            )
        )
        .all()
    )


# =====================================================
# UPDATE DEVICE STATUS
# =====================================================

def update_device_status(
    db: Session,
    hostname: str,
    status: str
):

    db_device = (
        db.query(DeviceDB)
        .filter(DeviceDB.hostname == hostname)
        .first()
    )

    if not db_device:
        return {
            "success": False,
            "message": "Device Not Found"
        }

    db_device.status = status

    db.commit()
    db.refresh(db_device)

    return db_device