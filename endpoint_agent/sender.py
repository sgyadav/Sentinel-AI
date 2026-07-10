import requests
from config import SERVER_URL


def send_data(data):

    try:

        response = requests.post(
            SERVER_URL,
            json=data,
            timeout=5
        )

        print("Connected to Server")

        print(response.json())

    except Exception as e:

        print("Backend Offline")

        print(e)