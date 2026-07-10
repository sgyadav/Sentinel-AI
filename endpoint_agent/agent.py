import time

from detection_engine import analyze
from collector import get_system_info
from sender import send_data
from config import HEARTBEAT_INTERVAL


print("=" * 50)
print("Sentinel Endpoint Agent Started")
print("=" * 50)


while True:

    system_data = get_system_info()

    incidents = analyze(system_data)

    system_data["incidents"] = incidents

    print(system_data)

    send_data(system_data)

    time.sleep(HEARTBEAT_INTERVAL)