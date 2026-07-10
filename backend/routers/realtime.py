"""Real-time dashboard and monitoring endpoints"""

import logging
from fastapi import APIRouter, WebSocket, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from db.database import get_db
from db.models import (
    EmployeeDB, DeviceDB, IncidentDB, TelemetryDB,
    SecurityEventDB, DeviceAssignmentDB
)
from core.security import get_current_user
from services.websocket_manager import manager
from detection.threat_detector import ThreatDetector

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/realtime",
    tags=["Real-time Dashboard"]
)

threat_detector = ThreatDetector()


# ===========================
# WebSocket Endpoints
# ===========================

@router.websocket("/ws/dashboard/{client_id}")
async def websocket_dashboard(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time dashboard updates
    
    Connects client and broadcasts:
    - Threat alerts
    - Device status changes
    - Incidents
    - Dashboard statistics
    """
    client_id = await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            
            # Handle ping/pong
            if data == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                    client_id
                )
    
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
    
    finally:
        manager.disconnect(client_id, websocket)


@router.websocket("/ws/incidents/{client_id}")
async def websocket_incidents(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for live incident stream"""
    client_id = await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send_personal_message(
                    {"type": "pong"},
                    client_id
                )
    
    except Exception:
        pass
    
    finally:
        manager.disconnect(client_id, websocket)


@router.websocket("/ws/telemetry/{client_id}")
async def websocket_telemetry(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for device telemetry stream"""
    client_id = await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send_personal_message(
                    {"type": "pong"},
                    client_id
                )
    
    except Exception:
        pass
    
    finally:
        manager.disconnect(client_id, websocket)


# ===========================
# Real-time Statistics Endpoints
# ===========================

@router.get("/stats/threats")
async def get_threat_stats(
    hours: int = 24,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get threat statistics for the last N hours"""
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Get incidents by severity
        incidents = db.query(IncidentDB).filter(
            IncidentDB.created_at >= time_threshold
        ).all()
        
        critical_count = sum(1 for i in incidents if i.severity == "Critical")
        high_count = sum(1 for i in incidents if i.severity == "High")
        medium_count = sum(1 for i in incidents if i.severity == "Medium")
        low_count = sum(1 for i in incidents if i.severity == "Low")
        
        return {
            "time_range_hours": hours,
            "total_threats": len(incidents),
            "severity_breakdown": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get threat stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve threat statistics"
        )


@router.get("/stats/devices")
async def get_device_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get device health statistics"""
    try:
        devices = db.query(DeviceDB).all()
        
        online = sum(1 for d in devices if d.status == "Online")
        offline = sum(1 for d in devices if d.status == "Offline")
        healthy = sum(1 for d in devices if d.health_status == "Healthy")
        warning = sum(1 for d in devices if d.health_status == "Warning")
        critical = sum(1 for d in devices if d.health_status == "Critical")
        
        avg_cpu = sum(d.cpu_usage for d in devices) / len(devices) if devices else 0
        avg_ram = sum(d.ram_usage for d in devices) / len(devices) if devices else 0
        avg_disk = sum(d.disk_usage for d in devices) / len(devices) if devices else 0
        
        return {
            "total_devices": len(devices),
            "status": {
                "online": online,
                "offline": offline
            },
            "health": {
                "healthy": healthy,
                "warning": warning,
                "critical": critical
            },
            "average_metrics": {
                "cpu_usage": round(avg_cpu, 2),
                "ram_usage": round(avg_ram, 2),
                "disk_usage": round(avg_disk, 2)
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get device stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve device statistics"
        )


@router.get("/stats/employees")
async def get_employee_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get employee risk statistics"""
    try:
        employees = db.query(EmployeeDB).all()
        
        high_risk = sum(1 for e in employees if e.risk_level in ["High", "Critical"])
        medium_risk = sum(1 for e in employees if e.risk_level == "Medium")
        low_risk = sum(1 for e in employees if e.risk_level == "Low")
        
        avg_risk = sum(e.risk_score for e in employees) / len(employees) if employees else 0
        
        return {
            "total_employees": len(employees),
            "risk_distribution": {
                "critical": sum(1 for e in employees if e.risk_level == "Critical"),
                "high": sum(1 for e in employees if e.risk_level == "High"),
                "medium": medium_risk,
                "low": low_risk
            },
            "average_risk_score": round(avg_risk, 2)
        }
    
    except Exception as e:
        logger.error(f"Failed to get employee stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee statistics"
        )


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard overview"""
    try:
        # Get counts
        total_employees = db.query(EmployeeDB).count()
        total_devices = db.query(DeviceDB).count()
        total_incidents = db.query(IncidentDB).count()
        
        # Get active incidents
        open_incidents = db.query(IncidentDB).filter(
            IncidentDB.status.in_(["Open", "Investigating"])
        ).count()
        
        # Get recent threats
        recent_threats = db.query(IncidentDB).order_by(
            IncidentDB.created_at.desc()
        ).limit(5).all()
        
        # Get device status
        online_devices = db.query(DeviceDB).filter(DeviceDB.status == "Online").count()
        offline_devices = total_devices - online_devices
        
        # Get high-risk employees
        high_risk_employees = db.query(EmployeeDB).filter(
            EmployeeDB.risk_level.in_(["High", "Critical"])
        ).count()
        
        return {
            "summary": {
                "total_employees": total_employees,
                "total_devices": total_devices,
                "total_incidents": total_incidents,
                "open_incidents": open_incidents
            },
            "device_status": {
                "online": online_devices,
                "offline": offline_devices
            },
            "risk_summary": {
                "high_risk_employees": high_risk_employees
            },
            "recent_threats": [
                {
                    "id": t.incident_id,
                    "type": t.attack_type,
                    "severity": t.severity,
                    "created": t.created_at.isoformat() if t.created_at else None
                }
                for t in recent_threats
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard overview"
        )


@router.get("/active-incidents")
async def get_active_incidents(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active and recent incidents (real-time feed)"""
    try:
        incidents = db.query(IncidentDB).filter(
            IncidentDB.status.in_(["Open", "Investigating"])
        ).order_by(
            IncidentDB.created_at.desc()
        ).limit(limit).all()
        
        return {
            "total": len(incidents),
            "incidents": [
                {
                    "incident_id": i.incident_id,
                    "hostname": i.hostname,
                    "attack_type": i.attack_type,
                    "risk_score": i.risk_score,
                    "severity": i.severity,
                    "status": i.status,
                    "priority": i.priority,
                    "created_at": i.created_at.isoformat() if i.created_at else None
                }
                for i in incidents
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to get active incidents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve incidents"
        )


@router.get("/connection-status")
async def get_connection_status(current_user: dict = Depends(get_current_user)):
    """Get WebSocket connection status"""
    return {
        "connected_clients": manager.get_connection_count(),
        "realtime_enabled": True,
        "timestamp": datetime.utcnow().isoformat()
    }
