import os

SERVER_URL = os.getenv("SENTINEL_SERVER_URL", "https://sentinel-ai-fz5u.onrender.com").rstrip("/")
AGENT_TOKEN = os.getenv("SENTINEL_AGENT_TOKEN", "")

HEARTBEAT_ENDPOINT = "/heartbeat"

PROCESS_ENDPOINT = "/processes"

USB_ENDPOINT = "/usb-events"

ALERT_ENDPOINT = "/alerts"

SEND_INTERVAL = 5

AGENT_NAME = "Sentinel Agent"

AGENT_VERSION = "1.0.0"

VERIFY_SSL = True
