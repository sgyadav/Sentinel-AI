import requests
from config import SERVER_URL


def send_system_info(data):

    try:

        response = requests.post(
            f"{SERVER_URL}/agent/status",
            json=data,
            timeout=5
        )

        print("✅ Data Sent")
        print(response.json())

    except Exception as e:

        print("❌ Unable to connect to Sentinel AI Server")

        print(e)