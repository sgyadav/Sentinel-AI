from fastapi import APIRouter
from ai_analyst.analyst import generate_ai_analysis

router = APIRouter(
    prefix="/ai",
    tags=["AI Analyst"]
)


@router.post("/analyze")
def analyze(incident: dict):

    return generate_ai_analysis(incident)