"""
Phase 7: LOGIN/LOGOUT EVENT MONITORING
Captures and displays login/logout events for security audit trail
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import LoginHistoryDB

router = APIRouter(prefix="/login-events", tags=["login-events"])

def get_db():
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/log-login")
def log_login(
    username: str,
    ip_address: str,
    db: Session = Depends(get_db)
):
    """Record a login event"""
    try:
        login_record = LoginHistoryDB(
            username=username,
            login_time=datetime.utcnow(),
            ip_address=ip_address,
            status="Success"
        )
        db.add(login_record)
        db.commit()
        return {"success": True, "message": "Login recorded"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}


@router.post("/log-logout")
def log_logout(username: str, db: Session = Depends(get_db)):
    """Record a logout event and calculate session duration"""
    try:
        # Get last login record for this user
        last_login = db.query(LoginHistoryDB).filter(
            LoginHistoryDB.username == username,
            LoginHistoryDB.logout_time == None
        ).order_by(LoginHistoryDB.login_time.desc()).first()

        if last_login:
            logout_time = datetime.utcnow()
            last_login.logout_time = logout_time
            last_login.session_duration = int(
                (logout_time - last_login.login_time).total_seconds()
            )
            db.commit()
            return {
                "success": True,
                "message": "Logout recorded",
                "session_duration": last_login.session_duration
            }
        else:
            return {"success": False, "message": "No active session found"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}


@router.get("/history")
def get_login_history(
    username: str = None,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get login/logout history for audit trail"""
    try:
        query = db.query(LoginHistoryDB)

        if username:
            query = query.filter(LoginHistoryDB.username == username)

        # Filter by date range
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(LoginHistoryDB.created_at >= start_date)

        events = query.order_by(LoginHistoryDB.login_time.desc()).all()

        return {
            "total": len(events),
            "events": [
                {
                    "id": e.id,
                    "username": e.username,
                    "login_time": e.login_time.isoformat(),
                    "logout_time": e.logout_time.isoformat() if e.logout_time else None,
                    "ip_address": e.ip_address,
                    "status": e.status,
                    "session_duration": e.session_duration,
                    "created_at": e.created_at.isoformat()
                }
                for e in events
            ]
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/stats")
def get_login_stats(days: int = 7, db: Session = Depends(get_db)):
    """Get login statistics for the dashboard"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        # Total logins
        total_logins = db.query(LoginHistoryDB).filter(
            LoginHistoryDB.login_time >= start_date
        ).count()

        # Total logouts
        total_logouts = db.query(LoginHistoryDB).filter(
            LoginHistoryDB.logout_time != None,
            LoginHistoryDB.logout_time >= start_date
        ).count()

        # Average session duration
        sessions = db.query(LoginHistoryDB).filter(
            LoginHistoryDB.session_duration != None,
            LoginHistoryDB.logout_time >= start_date
        ).all()

        avg_duration = sum([s.session_duration for s in sessions]) / len(sessions) if sessions else 0

        # Failed logins
        failed_logins = db.query(LoginHistoryDB).filter(
            LoginHistoryDB.status == "Failed",
            LoginHistoryDB.login_time >= start_date
        ).count()

        return {
            "total_logins": total_logins,
            "total_logouts": total_logouts,
            "avg_session_duration_seconds": int(avg_duration),
            "failed_logins": failed_logins,
            "period_days": days
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/top-users")
def get_top_users(limit: int = 10, days: int = 7, db: Session = Depends(get_db)):
    """Get top users by login frequency"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        from sqlalchemy import func

        users = db.query(
            LoginHistoryDB.username,
            func.count(LoginHistoryDB.id).label('login_count')
        ).filter(
            LoginHistoryDB.login_time >= start_date
        ).group_by(
            LoginHistoryDB.username
        ).order_by(
            func.count(LoginHistoryDB.id).desc()
        ).limit(limit).all()

        return {
            "total": len(users),
            "users": [
                {
                    "username": u[0],
                    "login_count": u[1]
                }
                for u in users
            ]
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
