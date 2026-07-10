"""Pydantic models for Sentinel AI API"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, EmailStr, validator


# ==========================
# Device Models
# ==========================

class Device(BaseModel):
    """Device registration model"""
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., min_length=1, max_length=255)
    operating_system: str = Field(..., min_length=1, max_length=255)
    
    class Config:
        example = {
            "hostname": "PC-001",
            "ip_address": "192.168.1.100",
            "operating_system": "Windows 10"
        }


# ==========================
# Security Event Models
# ==========================

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
    
    class Config:
        example = {
            "hostname": "PC-001",
            "event_type": "Failed Login",
            "severity": "High",
            "description": "Multiple failed login attempts"
        }


# ==========================
# Employee Models
# ==========================

class Employee(BaseModel):
    """Employee registration model"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    department: str = Field(..., min_length=1, max_length=255)
    designation: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    
    class Config:
        example = {
            "employee_id": "EMP-001",
            "name": "John Doe",
            "department": "IT Security",
            "designation": "Security Analyst",
            "email": "john.doe@example.com"
        }


# ==========================
# Device Assignment Models
# ==========================

class DeviceAssignment(BaseModel):
    """Device assignment model"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    hostname: str = Field(..., min_length=1, max_length=255)
    
    class Config:
        example = {
            "employee_id": "EMP-001",
            "hostname": "PC-001"
        }


# ==========================
# Endpoint Agent Models
# ==========================

class AgentStatus(BaseModel):
    """Agent status model"""
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., min_length=1, max_length=255)
    operating_system: str = Field(..., min_length=1)
    cpu_usage: float = Field(..., ge=0, le=100)
    ram_usage: float = Field(..., ge=0, le=100)
    disk_usage: float = Field(..., ge=0, le=100)
    username: str = Field(..., min_length=1)
    status: str = Field(..., pattern=r'^(Online|Offline|Idle)$')
    mac_address: str = Field(default="", max_length=17)
    boot_time: float = Field(default=0)
    uptime_seconds: int = Field(default=0)
    
    running_processes: List[Dict] = Field(default_factory=list)
    network_connections: List[Dict] = Field(default_factory=list)
    security_events: List[Dict] = Field(default_factory=list)
    incidents: List[Dict] = Field(default_factory=list)


# ==========================
# Security Policy Models
# ==========================

class SecurityPolicy(BaseModel):
    """Security policy configuration model"""
    cpu_threshold: float = Field(..., ge=0, le=100)
    ram_threshold: float = Field(..., ge=0, le=100)
    disk_threshold: float = Field(..., ge=0, le=100)
    heartbeat_interval: int = Field(..., ge=5, le=3600)
    alert_level: str = Field(..., pattern=r'^(Low|Medium|High|Critical)$')


# ==========================
# Organization Models
# ==========================

class Organization(BaseModel):
    """Organization registration model"""
    organization_name: str = Field(..., min_length=1, max_length=255)
    admin_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    industry: str = Field(..., min_length=1, max_length=255)


# ==========================
# Incident Models
# ==========================

class Incident(BaseModel):
    """Incident model"""
    incident_id: str
    hostname: str
    attack_type: str
    risk_score: float
    status: str = Field(..., pattern=r'^(Open|Investigating|Resolved|Closed)$')
    recommendation: str
