import socket
import platform
import getpass
import psutil
import uuid
import time

from process_monitor import get_running_processes
from network_monitor import get_network_connections
from event_monitor import get_security_events


def get_system_info():

    hostname = socket.gethostname()

    try:
        ip_address = socket.gethostbyname(hostname)
    except Exception:
        ip_address = "Unknown"

    disk_path = "C:\\" if platform.system() == "Windows" else "/"

    return {

        "hostname": hostname,

        "ip_address": ip_address,

        "operating_system": platform.platform(),

        "username": getpass.getuser(),

        "cpu_usage": psutil.cpu_percent(interval=1),

        "ram_usage": psutil.virtual_memory().percent,

        "disk_usage": psutil.disk_usage(disk_path).percent,

        "status": "Online",

        "mac_address": ":".join(
            [
                "{:02x}".format((uuid.getnode() >> ele) & 0xff)
                for ele in range(40, -8, -8)
            ]
        ),

        "boot_time": psutil.boot_time(),

        "uptime_seconds": int(time.time() - psutil.boot_time()),

        "running_processes": get_running_processes(),

        "network_connections": get_network_connections(),

        "security_events": get_security_events()

    }
