from fastapi import APIRouter

from soar.responder import decide_response

router = APIRouter(
    prefix="/soar",
    tags=["SOAR Engine"]
)


@router.post("/respond")
def respond(incident: dict):

    return decide_response(incident)