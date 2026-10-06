import requests
from config import SERVER_URL, AGENT_TOKEN


def send_data(data):

    try:

        response = requests.post(
            SERVER_URL,
            json=data,
            headers={"Authorization": f"Bearer {AGENT_TOKEN}"} if AGENT_TOKEN else {},
            timeout=5
        )

        print("Connected to Server")

        print(response.json())

    except Exception as e:

        print("Backend Offline")

        print(e)
