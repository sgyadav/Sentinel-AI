import socket
import platform
import psutil
import getpass


def get_system_info():

    hostname = socket.gethostname()

    ip_address = socket.gethostbyname(hostname)

    operating_system = platform.system() + " " + platform.release()

    cpu_usage = psutil.cpu_percent(interval=1)

    ram_usage = psutil.virtual_memory().percent

    disk_usage = psutil.disk_usage("/").percent

    username = getpass.getuser()

    return {

        "hostname": hostname,

        "ip_address": ip_address,

        "operating_system": operating_system,

        "cpu_usage": cpu_usage,

        "ram_usage": ram_usage,

        "disk_usage": disk_usage,

        "username": username,

        "status": "Online"

    }