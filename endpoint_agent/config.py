import os

SERVER_URL = os.getenv(
    "SENTINEL_SERVER_URL",
    "http://127.0.0.1:8000/agent/status"
)

HEARTBEAT_INTERVAL = int(os.getenv("SENTINEL_HEARTBEAT_INTERVAL", "5"))

AGENT_NAME = "Sentinel Endpoint Agent"

VERSION = "1.0"
