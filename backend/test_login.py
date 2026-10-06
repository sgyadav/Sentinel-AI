import requests
import os

password = os.getenv("SENTINEL_ADMIN_PASSWORD")
if not password:
    raise SystemExit("Set SENTINEL_ADMIN_PASSWORD to the existing admin password first")

response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": os.getenv("SENTINEL_ADMIN_USER", "admin"), "password": password}
)

print(f"Status: {response.status_code}")
if response.ok:
    print(f"Authenticated user: {response.json().get('user', {}).get('username', 'unknown')}")
else:
    print("Login failed; response body omitted to avoid logging sensitive details")
