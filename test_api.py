"""Manually smoke-check the local API using configured admin credentials."""

import os
import sys

import requests


BASE_URL = os.getenv("SENTINEL_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_USER = os.getenv("SENTINEL_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("SENTINEL_ADMIN_PASSWORD")


def main() -> int:
    if not ADMIN_PASSWORD:
        print("Set SENTINEL_ADMIN_PASSWORD to the existing admin password first")
        return 2

    session = requests.Session()
    login = session.post(
        f"{BASE_URL}/auth/login",
        json={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
        timeout=10,
    )
    if login.status_code != 200:
        print(f"[FAIL] POST /auth/login returned {login.status_code}")
        return 1

    session.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
    failures = 0
    for path in (
        "/health",
        "/employees",
        "/devices",
        "/assignments",
        "/threats",
        "/dashboard",
        "/employee-monitoring",
        "/settings",
        "/usb-events",
        "/processes/live",
        "/notifications",
    ):
        response = session.get(f"{BASE_URL}{path}", timeout=10)
        ok = response.status_code == 200
        print(f"[{'PASS' if ok else 'FAIL'}] GET {path}: {response.status_code}")
        failures += not ok
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
