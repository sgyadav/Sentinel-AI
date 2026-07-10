from sqlalchemy.orm import Session
from sqlalchemy import or_

from db.models import IncidentDB


# =========================================================
# CREATE INCIDENT
# =========================================================

def create_incident(db: Session, incident):

    db_incident = IncidentDB(
        incident_id=incident.incident_id,
        hostname=incident.hostname,
        attack_type=incident.attack_type,
        risk_score=incident.risk_score,
        status=incident.status,
        recommendation=incident.recommendation
    )

    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return db_incident


# =========================================================
# GET ALL INCIDENTS
# =========================================================

def get_all_incidents(db: Session):

    return db.query(IncidentDB).all()


# =========================================================
# GET SINGLE INCIDENT
# =========================================================

def get_incident(db: Session, incident_id: str):

    return (
        db.query(IncidentDB)
        .filter(
            IncidentDB.incident_id == incident_id
        )
        .first()
    )


# =========================================================
# UPDATE INCIDENT
# =========================================================

def update_incident(
    db: Session,
    incident_id: str,
    incident
):

    db_incident = (
        db.query(IncidentDB)
        .filter(
            IncidentDB.incident_id == incident_id
        )
        .first()
    )

    if not db_incident:

        return {
            "success": False,
            "message": "Incident Not Found"
        }

    db_incident.hostname = incident.hostname
    db_incident.attack_type = incident.attack_type
    db_incident.risk_score = incident.risk_score
    db_incident.status = incident.status
    db_incident.recommendation = incident.recommendation

    db.commit()
    db.refresh(db_incident)

    return db_incident


# =========================================================
# DELETE INCIDENT
# =========================================================

def delete_incident(
    db: Session,
    incident_id: str
):

    db_incident = (
        db.query(IncidentDB)
        .filter(
            IncidentDB.incident_id == incident_id
        )
        .first()
    )

    if not db_incident:

        return {
            "success": False,
            "message": "Incident Not Found"
        }

    db.delete(db_incident)

    db.commit()

    return {
        "success": True,
        "message": "Incident Deleted Successfully"
    }


# =========================================================
# CLOSE INCIDENT
# =========================================================

def close_incident(
    db: Session,
    incident_id: str
):

    db_incident = (
        db.query(IncidentDB)
        .filter(
            IncidentDB.incident_id == incident_id
        )
        .first()
    )

    if not db_incident:

        return {
            "success": False,
            "message": "Incident Not Found"
        }

    db_incident.status = "Closed"

    db.commit()

    db.refresh(db_incident)

    return db_incident


# =========================================================
# SEARCH INCIDENT
# =========================================================

def search_incident(
    db: Session,
    keyword: str
):

    return (
        db.query(IncidentDB)
        .filter(
            or_(
                IncidentDB.incident_id.contains(keyword),
                IncidentDB.hostname.contains(keyword),
                IncidentDB.attack_type.contains(keyword),
                IncidentDB.status.contains(keyword)
            )
        )
        .all()
    )