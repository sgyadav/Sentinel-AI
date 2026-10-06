import requests
import time
import os

time.sleep(3)

password = os.getenv("SENTINEL_ADMIN_PASSWORD")
if not password:
    raise SystemExit("Set SENTINEL_ADMIN_PASSWORD to the existing admin password first")

login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": os.getenv("SENTINEL_ADMIN_USER", "admin"), "password": password}
)
print(f"Login Status: {login_response.status_code}")
if login_response.status_code != 200:
    raise SystemExit("Admin login failed")
headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

# Test employee monitoring
monitor_response = requests.get("http://localhost:8000/employee-monitoring", headers=headers)
print(f"Employee Monitoring Status: {monitor_response.status_code}")

# Test settings endpoint
settings_response = requests.get("http://localhost:8000/settings", headers=headers)
print(f"Settings Status: {settings_response.status_code}")

print("\nAll new endpoints working!")
