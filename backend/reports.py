"""
Phase 8: REPORT GENERATION
Generate PDF and CSV reports for employees, endpoints, USB, threats, and daily security reports
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import csv
import io
from datetime import datetime, timedelta
from models import EmployeeDB, DeviceDB, USBEventDB, ThreatDB, ProcessDB

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

router = APIRouter(prefix="/reports", tags=["reports"])

def get_db():
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============= CSV REPORTS =============

@router.get("/employee-csv")
def export_employee_csv(db: Session = Depends(get_db)):
    """Export employee list as CSV"""
    try:
        employees = db.query(EmployeeDB).all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Headers
        writer.writerow([
            'Employee ID', 'Name', 'Email', 'Phone', 'Department',
            'Designation', 'Risk Score', 'Created At'
        ])

        # Data
        for emp in employees:
            writer.writerow([
                emp.employee_id,
                emp.name,
                emp.email,
                emp.phone,
                emp.department,
                emp.designation,
                emp.risk_score,
                emp.created_at.isoformat()
            ])

        return {
            "success": True,
            "format": "csv",
            "data": output.getvalue(),
            "filename": f"employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/endpoint-csv")
def export_endpoint_csv(db: Session = Depends(get_db)):
    """Export endpoints list as CSV"""
    try:
        devices = db.query(DeviceDB).all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Headers
        writer.writerow([
            'Device ID', 'Hostname', 'IP Address', 'MAC Address', 'OS',
            'OS Version', 'CPU %', 'RAM %', 'Disk %', 'Status', 'Last Heartbeat'
        ])

        # Data
        for dev in devices:
            writer.writerow([
                dev.device_id,
                dev.hostname,
                dev.ip_address,
                dev.mac_address,
                dev.operating_system,
                dev.os_version,
                f"{dev.cpu_usage:.1f}",
                f"{dev.ram_usage:.1f}",
                f"{dev.disk_usage:.1f}",
                dev.status,
                dev.last_heartbeat.isoformat() if dev.last_heartbeat else "Never"
            ])

        return {
            "success": True,
            "format": "csv",
            "data": output.getvalue(),
            "filename": f"endpoints_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/usb-csv")
def export_usb_csv(days: int = 7, db: Session = Depends(get_db)):
    """Export USB events as CSV"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        events = db.query(USBEventDB).filter(
            USBEventDB.event_time >= start_date
        ).all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Headers
        writer.writerow(['Action', 'Device', 'Hostname', 'Username', 'Event Time'])

        # Data
        for event in events:
            writer.writerow([
                event.action,
                event.device,
                event.hostname,
                event.username,
                event.event_time.isoformat()
            ])

        return {
            "success": True,
            "format": "csv",
            "data": output.getvalue(),
            "filename": f"usb_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/threat-csv")
def export_threat_csv(db: Session = Depends(get_db)):
    """Export threats as CSV"""
    try:
        threats = db.query(ThreatDB).all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Headers
        writer.writerow([
            'Threat ID', 'Device ID', 'Threat Name', 'Type', 'Severity',
            'Risk Score', 'Status', 'Detected At'
        ])

        # Data
        for threat in threats:
            writer.writerow([
                threat.threat_id,
                threat.device_id,
                threat.threat_name,
                threat.threat_type,
                threat.severity,
                threat.risk_score,
                threat.status,
                threat.detected_at.isoformat()
            ])

        return {
            "success": True,
            "format": "csv",
            "data": output.getvalue(),
            "filename": f"threats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


# ============= PDF REPORTS (if reportlab available) =============

@router.get("/daily-summary-pdf")
def export_daily_summary_pdf(db: Session = Depends(get_db)):
    """Generate daily security summary PDF"""
    if not REPORTLAB_AVAILABLE:
        return {
            "success": False,
            "message": "ReportLab not installed. Install with: pip install reportlab"
        }

    try:
        # Collect data
        total_employees = db.query(EmployeeDB).count()
        total_devices = db.query(DeviceDB).count()
        online_devices = db.query(DeviceDB).filter(DeviceDB.status == "Online").count()
        total_threats = db.query(ThreatDB).count()
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_usb_events = db.query(USBEventDB).filter(
            USBEventDB.event_time >= today_start
        ).count()

        # Generate PDF
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []

        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=1  # Center
        )

        elements.append(Paragraph("SENTINEL AI - Daily Security Report", title_style))
        elements.append(Spacer(1, 0.3*inch))

        # Report date
        date_text = f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(date_text, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Employees', str(total_employees)],
            ['Total Endpoints', str(total_devices)],
            ['Online Endpoints', str(online_devices)],
            ['Offline Endpoints', str(total_devices - online_devices)],
            ['Active Threats', str(total_threats)],
            ['USB Events (Today)', str(today_usb_events)],
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))

        # Status
        status = "OPERATIONAL" if total_threats == 0 else "ALERT"
        status_text = f"System Status: {status}"
        elements.append(Paragraph(status_text, styles['Heading2']))

        # Build PDF
        doc.build(elements)

        return {
            "success": True,
            "format": "pdf",
            "data": output.getvalue().hex(),  # Encode as hex for JSON serialization
            "filename": f"daily_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


# ============= REPORT METADATA =============

@router.get("/available-reports")
def get_available_reports():
    """List all available report types"""
    return {
        "csv_reports": [
            {"name": "Employee Report", "endpoint": "/reports/employee-csv", "format": "CSV"},
            {"name": "Endpoint Report", "endpoint": "/reports/endpoint-csv", "format": "CSV"},
            {"name": "USB Activity Report", "endpoint": "/reports/usb-csv", "format": "CSV", "params": "days=7"},
            {"name": "Threat Report", "endpoint": "/reports/threat-csv", "format": "CSV"},
        ],
        "pdf_reports": [
            {"name": "Daily Security Summary", "endpoint": "/reports/daily-summary-pdf", "format": "PDF"},
        ],
        "note": "PDF reports require: pip install reportlab"
    }
