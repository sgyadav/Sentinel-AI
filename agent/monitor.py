import socket
import platform
import psutil
import getpass
import uuid
import datetime


def get_system_info():

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    operating_system = platform.system() + " " + platform.release()
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent
    username = getpass.getuser()

    return {
        "device_uuid": str(uuid.getnode()),
        "hostname": hostname,
        "ip_address": ip_address,
        "operating_system": operating_system,
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "disk_usage": disk_usage,
        "username": username,
        "cpu_cores": psutil.cpu_count(),
        "total_ram": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "available_ram": round(psutil.virtual_memory().available / (1024 ** 3), 2),
        "boot_time": datetime.datetime.fromtimestamp(
            psutil.boot_time()
        ).isoformat(),
        "last_seen": datetime.datetime.now().isoformat(),
        "status": "Online"
    }