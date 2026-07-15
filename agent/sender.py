import requests

from config import (
    SERVER_URL,
    HEARTBEAT_ENDPOINT,
    PROCESS_ENDPOINT,
    USB_ENDPOINT,
)


def send_system_info(data):

    try:

        response = requests.post(
            f"{SERVER_URL}{HEARTBEAT_ENDPOINT}",
            json=data,
            timeout=5,
        )

        print("✅ Data Sent")
        print(response.json())

    except Exception as e:

        print("❌ Unable to connect to Sentinel AI Server")
        print(e)


def send_processes(processes, hostname=None, agent_id=None):

    try:
        payload = processes
        if isinstance(processes, list):
            payload = {
                "agent_id": agent_id or "",
                "hostname": hostname or (processes[0].get("hostname") if processes else "Unknown"),
                "processes": processes,
            }

        response = requests.post(
            f"{SERVER_URL}{PROCESS_ENDPOINT}",
            json=payload,
            timeout=10,
        )

        print("✅ Processes Sent")
        print(response.json())

    except Exception as e:

        print("❌ Unable to send process list")
        print(e)


def send_usb_event(event):

    try:

        response = requests.post(
            f"{SERVER_URL}{USB_ENDPOINT}",
            json=event,
            timeout=5,
        )

        print("✅ USB Event Sent")
        print(response.json())

    except Exception as e:

        print("❌ Unable to send USB event")
        print(e)
