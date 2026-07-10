from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models import SecurityPolicy
from services.security_policy_service import (
    get_policy,
    update_policy
)

router = APIRouter(
    prefix="/security-policy",
    tags=["Security Policy"]
)


@router.get("/")
def read_policy(
    db: Session = Depends(get_db)
):

    return get_policy(db)


@router.put("/")
def edit_policy(
    policy: SecurityPolicy,
    db: Session = Depends(get_db)
):

    return update_policy(db, policy)