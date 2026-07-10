from fastapi import APIRouter

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

notifications = []

@router.get("/")
def get_notifications():
    return notifications

@router.post("/add")
def add_notification(message: str):

    notification = {
        "id": len(notifications) + 1,
        "message": message,
        "status": "Unread"
    }

    notifications.append(notification)

    return {
        "message": "Notification Added",
        "notification": notification
    }