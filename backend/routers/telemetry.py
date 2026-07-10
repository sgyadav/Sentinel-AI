from fastapi import APIRouter
from storage import agent_status

router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"]
)

@router.get("/")
def get_telemetry():
    return agent_status