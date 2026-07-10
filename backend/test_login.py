import requests
import json

response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "Admin1234"}
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
