"""Enhanced Database Models with Real Data"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from datetime import datetime
from .base import Base


class OrganizationDB(Base):
    """Organization model"""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    industry = Column(String(100))
    website = Column(String(255))
    employees_count = Column(Integer, default=0)
    devices_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserDB(Base):
    """User account model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), ForeignKey("organizations.org_id"), nullable=False)
    username = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    
    role = Column(String(50), default="User")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    # Password reset
    reset_token = Column(String(255))
    reset_token_expires = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('org_id', 'username', name='_org_username_uc'),)


class EmployeeDB(Base):
    """Employee model"""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), ForeignKey("organizations.org_id"), nullable=False)
    employee_id = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    manager_id = Column(String(50))
    
    # Monitoring
    risk_score = Column(Float, default=0)
    risk_level = Column(String(50), default="Low")
    threat_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('org_id', 'employee_id', name='_org_emp_uc'),)


class DeviceDB(Base):
    """Device model with real monitoring"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), ForeignKey("organizations.org_id"), nullable=False)
    device_id = Column(String(100), unique=True, nullable=False, index=True)
    hostname = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(15), nullable=False)
    mac_address = Column(String(17))
    
    # Device Info
    operating_system = Column(String(100))
    os_version = Column(String(50))
    device_type = Column(String(50))  # Laptop, Desktop, Server, Mobile
    
    # Hardware
    cpu_cores = Column(Integer)
    total_ram = Column(Integer)
    total_disk = Column(Integer)
    
    # Real-time Metrics
    cpu_usage = Column(Float, default=0)
    ram_usage = Column(Float, default=0)
    disk_usage = Column(Float, default=0)
    network_usage = Column(Float, default=0)
    
    # Status
    status = Column(String(50), default="Online")  # Online, Offline, Idle
    health_status = Column(String(50), default="Healthy")
    
    # Security
    antivirus_enabled = Column(Boolean, default=True)
    firewall_enabled = Column(Boolean, default=True)
    updates_available = Column(Integer, default=0)
    threat_count = Column(Integer, default=0)
    
    # Tracking
    last_heartbeat = Column(DateTime(timezone=True))
    last_scan = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeviceAssignmentDB(Base):
    """Device assignment to employees"""
    __tablename__ = "device_assignments"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), ForeignKey("organizations.org_id"), nullable=False)
    employee_id = Column(String(50), nullable=False, index=True)
    device_id = Column(String(100), ForeignKey("devices.device_id"), nullable=False)
    
    assignment_date = Column(DateTime(timezone=True), server_default=func.now())
    unassignment_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ThreatDB(Base):
    """Real threats detected"""
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), ForeignKey("organizations.org_id"), nullable=False)
    threat_id = Column(String(100), unique=True, nullable=False, index=True)
    
    device_id = Column(String(100), ForeignKey("devices.device_id"), nullable=False)
    threat_name = Column(String(255), nullable=False)
    threat_type = Column(String(100), nullable=False)  # Malware, Ransomware, Spyware, etc.
    
    severity = Column(String(50), default="Medium")  # Critical, High, Medium, Low
    confidence = Column(Float, default=0)
    risk_score = Column(Float, default=0)
    
    # Detection Details
    detection_method = Column(String(100))
    file_path = Column(Text)
    file_hash = Column(String(255))
    
    # Status
    status = Column(String(50), default="Detected")  # Detected, Quarantined, Removed, Ignored
    action_taken = Column(Text)
    
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScanResultDB(Base):
    """Real-time scan results"""
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), ForeignKey("organizations.org_id"), nullable=False)
    device_id = Column(String(100), ForeignKey("devices.device_id"), nullable=False)
    
    scan_type = Column(String(50))  # Full, Quick, Custom
    scan_status = Column(String(50), default="Running")  # Running, Completed, Failed
    
    total_files_scanned = Column(Integer, default=0)
    threats_detected = Column(Integer, default=0)
    threats_quarantined = Column(Integer, default=0)
    
    scan_duration = Column(Integer)  # seconds
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    results = Column(JSON)  # Detailed results


class MonitoringDataDB(Base):
    """Real monitoring data for devices"""
    __tablename__ = "monitoring_data"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), ForeignKey("organizations.org_id"), nullable=False)
    device_id = Column(String(100), ForeignKey("devices.device_id"), nullable=False)
    
    # Metrics
    cpu_usage = Column(Float)
    ram_usage = Column(Float)
    disk_usage = Column(Float)
    network_in = Column(Float)  # MB/s
    network_out = Column(Float)  # MB/s
    
    # Processes
    process_count = Column(Integer)
    running_processes = Column(JSON)
    suspicious_processes = Column(JSON)
    
    # Network
    open_ports = Column(JSON)
    active_connections = Column(JSON)
    suspicious_ips = Column(JSON)
    
    # System Events
    login_attempts = Column(Integer, default=0)
    failed_logins = Column(Integer, default=0)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class IncidentDB(Base):
    """Security incidents"""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), ForeignKey("organizations.org_id"), nullable=False)
    incident_id = Column(String(100), unique=True, nullable=False, index=True)
    
    threat_id = Column(String(100), ForeignKey("threats.threat_id"))
    device_id = Column(String(100), ForeignKey("devices.device_id"))
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    threat_type = Column(String(100))
    
    severity = Column(String(50), default="Medium")
    risk_score = Column(Float, default=0)
    status = Column(String(50), default="Open")  # Open, Investigating, Resolved, Closed
    
    assigned_to = Column(String(255))
    resolved_by = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))


class ActivityLogDB(Base):
    """Activity and audit log"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), ForeignKey("organizations.org_id"), nullable=False)
    user_id = Column(String(255))
    
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    details = Column(JSON)
    
    ip_address = Column(String(15))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
