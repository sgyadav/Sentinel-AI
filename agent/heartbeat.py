import time

from monitor import get_system_info
from sender import send_system_info
from config import SEND_INTERVAL


def start_heartbeat():

    print("Sentinel Agent Started...")

    while True:

        system_info = get_system_info()

        send_system_info(system_info)

        time.sleep(SEND_INTERVAL)