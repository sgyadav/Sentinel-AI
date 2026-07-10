from sqlalchemy.orm import Session
from db.models import SecurityPolicyDB


def get_policy(db: Session):

    policy = db.query(SecurityPolicyDB).first()

    if policy is None:

        policy = SecurityPolicyDB()

        db.add(policy)

        db.commit()

        db.refresh(policy)

    return policy


def update_policy(db: Session, data):

    policy = get_policy(db)

    policy.cpu_threshold = data.cpu_threshold

    policy.ram_threshold = data.ram_threshold

    policy.disk_threshold = data.disk_threshold

    policy.heartbeat_interval = data.heartbeat_interval

    policy.alert_level = data.alert_level

    db.commit()

    db.refresh(policy)

    return policy