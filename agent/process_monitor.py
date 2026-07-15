import psutil
import datetime
import getpass
import socket
import time


def _current_username():
    try:
        return getpass.getuser()
    except Exception:
        return "Unknown"


def get_running_processes():

    process_list = []
    hostname = socket.gethostname()
    fallback_user = _current_username()

    primed = []
    for process in psutil.process_iter(['pid']):
        try:
            process.cpu_percent(None)
            primed.append(process)
        except Exception:
            continue

    time.sleep(0.25)

    for process in primed:

        try:
            info = process.as_dict(attrs=['pid', 'name', 'username', 'memory_percent'])
            name = info.get('name') or f"pid-{info.get('pid')}"
            username = info.get('username') or fallback_user

            process_list.append({

                "hostname": hostname,

                "pid": info.get('pid') or 0,

                "name": name,

                "process_name": name,

                "username": username,

                "user": username,

                "cpu_percent": round(float(process.cpu_percent(None) or 0), 2),

                "memory_percent": round(float(info.get('memory_percent') or 0), 3),

                "timestamp": datetime.datetime.now().isoformat()

            })

        except Exception:

            continue

    return sorted(
        process_list,
        key=lambda item: (item["cpu_percent"], item["memory_percent"]),
        reverse=True,
    )
