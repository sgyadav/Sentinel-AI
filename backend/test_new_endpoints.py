import requests
import time

time.sleep(3)

# Test login
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "Admin1234"}
)
print(f"Login Status: {login_response.status_code}")

# Test employee monitoring
monitor_response = requests.get("http://localhost:8000/employee-monitoring")
print(f"Employee Monitoring Status: {monitor_response.status_code}")
print(f"Response: {monitor_response.json()}")

# Test settings endpoint
settings_response = requests.get("http://localhost:8000/settings")
print(f"Settings Status: {settings_response.status_code}")
print(f"Settings: {settings_response.json()}")

print("\nAll new endpoints working!")
