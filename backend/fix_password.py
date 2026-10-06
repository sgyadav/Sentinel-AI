"""Reset the local admin password after explicitly setting an environment variable."""

import os
from pathlib import Path

from sqlalchemy import create_engine, text

from auth.password import hash_password
from core.config import normalize_database_url


def main() -> None:
    new_password = os.getenv("SENTINEL_RESET_ADMIN_PASSWORD")
    if not new_password:
        raise SystemExit(
            "Set SENTINEL_RESET_ADMIN_PASSWORD before running this password reset utility"
        )

    database_url = normalize_database_url(
        os.getenv("DATABASE_URL", f"sqlite:///{Path(__file__).with_name('sentinel.db').as_posix()}")
    )
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
    )
    with engine.begin() as connection:
        result = connection.execute(
            text("UPDATE users SET password = :password WHERE username = :username"),
            {"password": hash_password(new_password), "username": "admin"},
        )
        if result.rowcount == 0:
            raise SystemExit("No admin row was updated")

    print("Admin password reset successfully")


if __name__ == "__main__":
    main()
