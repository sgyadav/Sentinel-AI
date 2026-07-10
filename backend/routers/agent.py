"""Agent telemetry and heartbeat endpoints"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from db.database import get_db
from db.models import DeviceDB, TelemetryDB
from services.websocket_manager import manager
from pydantic import BaseModel
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/agent",
    tags=["Endpoint Agent"]
)


class TelemtryData(BaseModel):
    """Telemetry data from agent"""
    agent_version: str
    timestamp: str
    system_info: Dict[str, Any]
    performance: Dict[str, Any]
    processes: List[Dict[str, Any]]
    network_connections: List[Dict[str, Any]]
    security_status: Dict[str, Any]


class HeartbeatData(BaseModel):
    """Agent heartbeat"""
    hostname: str
    ip_address: str
    timestamp: str
    status: str


@router.post("/telemetry")
async def receive_telemetry(
    data: TelemtryData,
    db: Session = Depends(get_db)
):
    """Receive telemetry from Windows Endpoint Agent"""
    try:
        system_info = data.system_info
        hostname = system_info.get("hostname", "")
        
        # Get or create device
        device = db.query(DeviceDB).filter(DeviceDB.hostname == hostname).first()
        
        if not device:
            device = DeviceDB(
                hostname=hostname,
                ip_address=system_info.get("ip_address", ""),
                mac_address=system_info.get("mac_address", ""),
                operating_system=system_info.get("os", "Windows"),
                os_version=system_info.get("platform", ""),
                cpu_cores=system_info.get("cpu_cores", 0),
                total_ram=system_info.get("total_ram", 0),
                total_disk=system_info.get("total_disk", 0),
                agent_version=data.agent_version,
                status="Online",
                health_status="Healthy"
            )
            db.add(device)
        else:
            # Update device info
            device.ip_address = system_info.get("ip_address", device.ip_address)
            device.agent_version = data.agent_version
            device.status = "Online"
            device.last_heartbeat = datetime.utcnow()
        
        # Update performance metrics
        perf = data.performance
        device.cpu_usage = perf.get("cpu_usage", 0)
        device.ram_usage = perf.get("ram_usage", 0)
        device.disk_usage = perf.get("disk_usage", 0)
        device.last_sync = datetime.utcnow()
        
        # Determine health status
        if device.cpu_usage > 90 or device.ram_usage > 90:
            device.health_status = "Critical"
        elif device.cpu_usage > 75 or device.ram_usage > 75:
            device.health_status = "Warning"
        else:
            device.health_status = "Healthy"
        
        # Update security status
        sec_status = data.security_status
        device.antivirus_enabled = sec_status.get("antivirus_enabled", True)
        device.firewall_enabled = sec_status.get("firewall_enabled", True)
        
        db.add(device)
        
        # Store telemetry
        telemetry = TelemetryDB(
            hostname=hostname,
            cpu_usage=device.cpu_usage,
            ram_usage=device.ram_usage,
            disk_usage=device.disk_usage,
            bytes_sent=perf.get("network_bytes_sent", 0),
            bytes_received=perf.get("network_bytes_received", 0),
            process_count=perf.get("process_count", 0),
            active_connections=len(data.network_connections)
        )
        db.add(telemetry)
        
        db.commit()
        
        # Broadcast telemetry update
        await manager.broadcast_telemetry({
            "hostname": hostname,
            "cpu_usage": device.cpu_usage,
            "ram_usage": device.ram_usage,
            "disk_usage": device.disk_usage,
            "health_status": device.health_status,
            "status": device.status,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Telemetry received from {hostname}")
        
        return {
            "success": True,
            "message": "Telemetry received",
            "device_id": device.id
        }
    
    except Exception as e:
        logger.error(f"Failed to process telemetry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process telemetry"
        )


@router.post("/heartbeat")
async def receive_heartbeat(
    data: HeartbeatData,
    db: Session = Depends(get_db)
):
    """Receive heartbeat from Windows Endpoint Agent"""
    try:
        hostname = data.hostname
        
        # Get or create device
        device = db.query(DeviceDB).filter(DeviceDB.hostname == hostname).first()
        
        if not device:
            device = DeviceDB(
                hostname=hostname,
                ip_address=data.ip_address,
                operating_system="Windows",
                status="Online"
            )
            db.add(device)
        else:
            device.status = data.status
            device.ip_address = data.ip_address
        
        device.last_heartbeat = datetime.utcnow()
        db.commit()
        
        logger.debug(f"Heartbeat received from {hostname}")
        
        return {
            "success": True,
            "server_time": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to process heartbeat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process heartbeat"
        )


@router.get("/devices/online")
async def get_online_devices(db: Session = Depends(get_db)):
    """Get all online devices"""
    try:
        devices = db.query(DeviceDB).filter(DeviceDB.status == "Online").all()
        
        return {
            "total": len(devices),
            "devices": [
                {
                    "hostname": d.hostname,
                    "ip_address": d.ip_address,
                    "status": d.status,
                    "cpu_usage": d.cpu_usage,
                    "ram_usage": d.ram_usage,
                    "disk_usage": d.disk_usage,
                    "last_heartbeat": d.last_heartbeat.isoformat() if d.last_heartbeat else None
                }
                for d in devices
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to get online devices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve online devices"
        )
