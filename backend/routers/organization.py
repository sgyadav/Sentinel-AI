from fastapi import APIRouter
from models import Organization
from storage import organizations

router = APIRouter(
    prefix="/organization",
    tags=["Organization"]
)

@router.post("/register")
def register_organization(org: Organization):

    organizations.clear()

    organizations.append(org.model_dump())

    return {
        "message": "Organization Registered",
        "organization": org
    }


@router.get("/")
def get_organization():

    if organizations:
        return organizations[0]

    return {}