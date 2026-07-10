from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os


def generate_incident_report(incidents):

    os.makedirs("generated_reports", exist_ok=True)

    filename = "generated_reports/Incident_Report.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>SENTINEL AI - Incident Report</b>", styles["Title"])
    )

    elements.append(
        Paragraph("Generated Automatically", styles["Normal"])
    )

    for incident in incidents:

        elements.append(

            Paragraph(

                f"""
                Incident ID : {incident['incident_id']}<br/>
                Host : {incident['hostname']}<br/>
                Attack : {incident['attack_type']}<br/>
                Risk Score : {incident['risk_score']}<br/>
                Status : {incident['status']}<br/>
                """,

                styles["BodyText"]

            )

        )

    doc.build(elements)

    return filename