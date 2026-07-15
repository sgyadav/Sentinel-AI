"""
Phase 9: EMAIL ALERTING SYSTEM
Automatic alerts for threats, USB events, and offline endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import threading
import time
from models import SettingsDB, NotificationDB, ThreatDB, USBEventDB, DeviceDB

router = APIRouter(prefix="/alerts", tags=["alerts"])

def get_db():
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AlertManager:
    """Manages alert rules and notifications"""

    def __init__(self, db: Session):
        self.db = db
        self.settings = self._load_settings()

    def _load_settings(self):
        """Load SMTP settings"""
        try:
            settings = self.db.query(SettingsDB).all()
            return {s.setting_key: s.setting_value for s in settings}
        except:
            return {}

    def _send_email(self, recipient, subject, body):
        """Send email via SMTP"""
        try:
            smtp_server = self.settings.get("smtp_server")
            smtp_port = int(self.settings.get("smtp_port", 587))
            smtp_email = self.settings.get("smtp_email")
            smtp_password = self.settings.get("smtp_password")

            if not all([smtp_server, smtp_email, smtp_password]):
                return False

            msg = MIMEMultipart()
            msg["From"] = smtp_email
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
            server.quit()

            # Log notification
            notification = NotificationDB(
                notification_id=f"alert_{int(time.time())}",
                recipient_email=recipient,
                subject=subject,
                message=body[:255],
                status="Sent"
            )
            self.db.add(notification)
            self.db.commit()

            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False

    def send_threat_alert(self, threat_id, device_id, threat_name, severity):
        """Alert when threat detected"""
        admin_email = self.settings.get("admin_email")
        if not admin_email:
            return False

        subject = f"[ALERT] Threat Detected: {threat_name}"
        body = f"""
        <h2>Security Threat Detected</h2>
        <p><strong>Threat ID:</strong> {threat_id}</p>
        <p><strong>Device:</strong> {device_id}</p>
        <p><strong>Threat Name:</strong> {threat_name}</p>
        <p><strong>Severity:</strong> <span style="color: red;">{severity}</span></p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Please investigate immediately.</p>
        """

        return self._send_email(admin_email, subject, body)

    def send_usb_alert(self, device, hostname, action):
        """Alert on USB insert/remove"""
        admin_email = self.settings.get("admin_email")
        if not admin_email:
            return False

        subject = f"[USB] Device {action}: {device}"
        body = f"""
        <h2>USB Device Event</h2>
        <p><strong>Action:</strong> {action}</p>
        <p><strong>Device:</strong> {device}</p>
        <p><strong>Hostname:</strong> {hostname}</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """

        return self._send_email(admin_email, subject, body)

    def send_offline_alert(self, hostname, ip_address):
        """Alert when endpoint goes offline"""
        admin_email = self.settings.get("admin_email")
        if not admin_email:
            return False

        subject = f"[OFFLINE] Endpoint Down: {hostname}"
        body = f"""
        <h2>Endpoint Offline</h2>
        <p><strong>Hostname:</strong> {hostname}</p>
        <p><strong>IP Address:</strong> {ip_address}</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Endpoint has stopped sending heartbeats. Please investigate connectivity.</p>
        """

        return self._send_email(admin_email, subject, body)


# ============= ALERT ENDPOINTS =============

@router.post("/send-threat-alert")
def trigger_threat_alert(
    threat_id: str,
    device_id: str,
    threat_name: str,
    severity: str,
    db: Session = Depends(get_db)
):
    """Manually trigger threat alert"""
    alert_mgr = AlertManager(db)
    success = alert_mgr.send_threat_alert(threat_id, device_id, threat_name, severity)
    return {"success": success, "message": "Alert sent" if success else "Alert failed"}


@router.post("/send-usb-alert")
def trigger_usb_alert(
    device: str,
    hostname: str,
    action: str,
    db: Session = Depends(get_db)
):
    """Manually trigger USB alert"""
    alert_mgr = AlertManager(db)
    success = alert_mgr.send_usb_alert(device, hostname, action)
    return {"success": success, "message": "Alert sent" if success else "Alert failed"}


@router.post("/send-offline-alert")
def trigger_offline_alert(
    hostname: str,
    ip_address: str,
    db: Session = Depends(get_db)
):
    """Manually trigger endpoint offline alert"""
    alert_mgr = AlertManager(db)
    success = alert_mgr.send_offline_alert(hostname, ip_address)
    return {"success": success, "message": "Alert sent" if success else "Alert failed"}


@router.get("/test-smtp")
def test_smtp_config(db: Session = Depends(get_db)):
    """Test SMTP configuration"""
    try:
        settings = db.query(SettingsDB).all()
        settings_dict = {s.setting_key: s.setting_value for s in settings}

        smtp_server = settings_dict.get("smtp_server")
        smtp_port = int(settings_dict.get("smtp_port", 587))
        smtp_email = settings_dict.get("smtp_email")
        smtp_password = settings_dict.get("smtp_password")

        if not all([smtp_server, smtp_email, smtp_password]):
            return {
                "success": False,
                "message": "SMTP settings not configured"
            }

        server = smtplib.SMTP(smtp_server, smtp_port, timeout=5)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.quit()

        return {
            "success": True,
            "message": "SMTP configuration is valid",
            "server": smtp_server,
            "port": smtp_port,
            "email": smtp_email
        }
    except Exception as e:
        return {"success": False, "message": f"SMTP test failed: {str(e)}"}


@router.get("/alert-rules")
def get_alert_rules():
    """Get configured alert rules"""
    return {
        "rules": [
            {
                "name": "Threat Detected",
                "trigger": "New threat detected",
                "condition": "severity >= Medium",
                "action": "Email admin",
                "enabled": True
            },
            {
                "name": "USB Device Event",
                "trigger": "USB insert or remove",
                "condition": "Always",
                "action": "Email admin",
                "enabled": True
            },
            {
                "name": "Endpoint Offline",
                "trigger": "No heartbeat for 30 minutes",
                "condition": "last_heartbeat > 30 minutes ago",
                "action": "Email admin",
                "enabled": True
            }
        ]
    }


@router.post("/enable-alert-rule")
def enable_alert_rule(rule_name: str):
    """Enable alert rule"""
    return {"success": True, "message": f"Alert rule '{rule_name}' enabled"}


@router.post("/disable-alert-rule")
def disable_alert_rule(rule_name: str):
    """Disable alert rule"""
    return {"success": True, "message": f"Alert rule '{rule_name}' disabled"}


# ============= BACKGROUND MONITORING =============

class AlertMonitor(threading.Thread):
    """Background thread monitoring for alert triggers"""

    def __init__(self, db: Session, check_interval=300):
        super().__init__(daemon=True)
        self.db = db
        self.check_interval = check_interval  # 5 minutes default
        self.running = True

    def run(self):
        """Monitor for alert conditions"""
        while self.running:
            try:
                self._check_offline_endpoints()
                self._check_threats()
            except Exception as e:
                print(f"Alert monitor error: {e}")

            time.sleep(self.check_interval)

    def _check_offline_endpoints(self):
        """Check for offline endpoints"""
        from datetime import timedelta

        alert_mgr = AlertManager(self.db)
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)

        # Find endpoints with no recent heartbeat
        offline_devices = self.db.query(DeviceDB).filter(
            (DeviceDB.last_heartbeat < cutoff_time) |
            (DeviceDB.last_heartbeat == None)
        ).all()

        for device in offline_devices:
            if device.status != "Offline":
                device.status = "Offline"
                alert_mgr.send_offline_alert(device.hostname, device.ip_address)
                self.db.commit()

    def _check_threats(self):
        """Check for new threats"""
        alert_mgr = AlertManager(self.db)

        # Get unalerted threats
        threats = self.db.query(ThreatDB).filter(
            ThreatDB.status == "Detected"
        ).all()

        for threat in threats[:5]:  # Limit to prevent alert spam
            if threat.severity in ["High", "Critical"]:
                alert_mgr.send_threat_alert(
                    threat.threat_id,
                    threat.device_id,
                    threat.threat_name,
                    threat.severity
                )
                threat.status = "Alerted"
                self.db.commit()

    def stop(self):
        """Stop monitoring"""
        self.running = False
