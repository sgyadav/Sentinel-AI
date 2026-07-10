from fastapi import APIRouter
from threat_intelligence.reputation import check_reputation

router = APIRouter(
    prefix="/threat-intel",
    tags=["Threat Intelligence"]
)


@router.get("/{ip_address}")
def threat_lookup(ip_address: str):

    return check_reputation(ip_address)