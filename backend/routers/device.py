from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models import Device

from services.device_service import (
    create_device,
    get_all_devices,
    get_device,
    update_device,
    delete_device,
    search_device,
    update_device_status
)

router = APIRouter(
    prefix="/device",
    tags=["Devices"]
)


# =====================================================
# REGISTER DEVICE
# =====================================================

@router.post("/register")
def register_device(
    device: Device,
    db: Session = Depends(get_db)
):
    return create_device(db, device)


# =====================================================
# GET ALL DEVICES
# =====================================================

@router.get("/")
def get_devices(
    db: Session = Depends(get_db)
):
    return get_all_devices(db)


# =====================================================
# GET SINGLE DEVICE
# =====================================================

@router.get("/{hostname}")
def get_single_device(
    hostname: str,
    db: Session = Depends(get_db)
):
    device = get_device(db, hostname)

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device Not Found"
        )

    return device


# =====================================================
# UPDATE DEVICE
# =====================================================

@router.put("/{hostname}")
def update_device_details(
    hostname: str,
    device: Device,
    db: Session = Depends(get_db)
):
    return update_device(
        db,
        hostname,
        device
    )


# =====================================================
# DELETE DEVICE
# =====================================================

@router.delete("/{hostname}")
def remove_device(
    hostname: str,
    db: Session = Depends(get_db)
):
    return delete_device(
        db,
        hostname
    )


# =====================================================
# SEARCH DEVICE
# =====================================================

@router.get("/search/{keyword}")
def search_devices(
    keyword: str,
    db: Session = Depends(get_db)
):
    return search_device(
        db,
        keyword
    )


# =====================================================
# UPDATE DEVICE STATUS
# =====================================================

@router.put("/{hostname}/status/{status}")
def change_status(
    hostname: str,
    status: str,
    db: Session = Depends(get_db)
):
    return update_device_status(
        db,
        hostname,
        status
    )