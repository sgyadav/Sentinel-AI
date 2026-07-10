from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from storage import incidents

router = APIRouter(
    prefix="/report",
    tags=["Reports"]
)


@router.get("/")
def report_status():

    return {
        "status": "Report Module Running"
    }


@router.get("/incident")
def incident_report():
    try:
        from reports.pdf_generator import generate_incident_report
    except ModuleNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail="PDF report generation dependency is not installed. Install backend requirements to enable reports."
        ) from error

    filename = generate_incident_report(incidents)

    return FileResponse(
        path=filename,
        filename="Incident_Report.pdf",
        media_type="application/pdf"
    )
