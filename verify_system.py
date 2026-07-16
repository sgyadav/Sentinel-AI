"""
SENTINEL AI system smoke check.

Runs a practical end-to-end API check against the backend:
- health
- admin login
- dashboard
- endpoint registration through heartbeat
- endpoint lookup
- SOC list APIs
- cleanup of the temporary verification endpoint
"""

import json
import os
import socket
import sys
import time
import uuid
from urllib import error, request


BASE_URL = os.getenv("SENTINEL_BASE_URL", "http://localhost:8000").rstrip("/")
ADMIN_USER = os.getenv("SENTINEL_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("SENTINEL_ADMIN_PASSWORD", "Admin1234")


def call(method, path, payload=None):
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
    with request.urlopen(req, timeout=10) as response:
        data = response.read().decode("utf-8")
        return response.status, json.loads(data) if data else {}


def check(name, method, path, payload=None):
    try:
        status, data = call(method, path, payload)
        if status != 200:
            raise RuntimeError(f"HTTP {status}")
        print(f"[PASS] {name}")
        return data
    except Exception as exc:
        print(f"[FAIL] {name}: {exc}")
        raise


def main():
    hostname = f"VERIFY-{socket.gethostname()}-{uuid.uuid4().hex[:6]}"
    mac_suffix = uuid.uuid4().hex[:12]
    mac = ":".join(mac_suffix[i:i + 2] for i in range(0, 12, 2))
    device_id = None

    try:
        check("backend health", "GET", "/health")
        check("admin login", "POST", "/auth/login", {
            "username": ADMIN_USER,
            "password": ADMIN_PASSWORD,
        })
        check("dashboard", "GET", "/dashboard")

        heartbeat = check("endpoint heartbeat registration", "POST", "/heartbeat", {
            "device_uuid": "GENERATE_NEW",
            "agent_id": "GENERATE_NEW",
            "hostname": hostname,
            "username": "SmokeTest",
            "ip_address": "127.0.0.1",
            "mac_address": mac,
            "operating_system": "Windows",
            "os_version": "Smoke",
            "device_type": "Laptop",
            "cpu_usage": 1.0,
            "ram_usage": 1.0,
            "disk_usage": 1.0,
            "agent_version": "smoke",
        })
        device_id = heartbeat.get("agent_id") or heartbeat.get("device_id")
        if not device_id:
            raise RuntimeError("heartbeat did not return agent_id/device_id")

        devices = check("endpoint visible in devices", "GET", f"/devices?search={hostname}")
        if devices.get("total", 0) < 1:
            raise RuntimeError("registered endpoint was not found in /devices")
        print(f"[PASS] registered endpoint id: {device_id}")

        check("live processes API", "GET", "/processes/live")
        check("USB API", "GET", "/usb-events?period=today")
        check("login history API", "GET", "/login-events?period=today")
        check("threats API", "GET", "/threats")
        check("audit log API", "GET", "/audit-logs")

        print("[PASS] Sentinel AI smoke check completed")
        return 0
    except Exception:
        print("[FAIL] Sentinel AI smoke check failed")
        return 1
    finally:
        if device_id:
            try:
                time.sleep(0.2)
                call("DELETE", f"/devices/{device_id}")
                print(f"[PASS] removed temporary endpoint: {device_id}")
            except Exception as exc:
                print(f"[WARN] could not remove temporary endpoint {device_id}: {exc}")


if __name__ == "__main__":
    sys.exit(main())
