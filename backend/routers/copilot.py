from fastapi import APIRouter
from ai_copilot.copilot import ask_ai

router = APIRouter(
    prefix="/copilot",
    tags=["AI Copilot"]
)


@router.get("/")
def chat(question: str):

    return ask_ai(question)