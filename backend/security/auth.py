from sqlalchemy.orm import Session

from services.user_service import get_user
from security.password import verify_password
from security.jwt_handler import create_access_token


def authenticate_user(
    db: Session,
    username: str,
    password: str
):

    user = get_user(db, username)

    if not user:
        return None

    if not verify_password(
        password,
        user.password
    ):
        return None

    token = create_access_token({

        "username": user.username,

        "role": user.role

    })

    return {

        "access_token": token,

        "token_type": "bearer",

        "role": user.role

    }