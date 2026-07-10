from sqlalchemy.orm import Session
from db.models import UserDB
from security.password import hash_password

def create_user(db: Session, user):

    db_user = UserDB(
        username=user.username,
        password=hash_password(user.password),
        role=user.role,
        organization="Sentinel AI"
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user(db: Session, username: str):

    return db.query(UserDB).filter(
        UserDB.username == username
    ).first()