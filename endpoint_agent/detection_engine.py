import re


SUSPICIOUS_PROCESS_NAMES = {
    "mimikatz.exe",
    "psexec.exe",
    "nc.exe",
    "netcat.exe",
    "procdump.exe",
    "rubeus.exe"
}


POWERSHELL_KEYWORDS = [
    "encodedcommand",
    "downloadstring",
    "iex",
    "invoke-expression"
]


def analyze(system_data):

    incidents = []

    # ------------------------------------
    # High CPU
    # ------------------------------------

    if system_data["cpu_usage"] >= 90:

        incidents.append({

            "severity": "High",

            "type": "High CPU Usage",

            "description": f"CPU Usage is {system_data['cpu_usage']}%"

        })

    # ------------------------------------
    # High RAM
    # ------------------------------------

    if system_data["ram_usage"] >= 90:

        incidents.append({

            "severity": "High",

            "type": "High Memory Usage",

            "description": f"RAM Usage is {system_data['ram_usage']}%"

        })

    # ------------------------------------
    # Disk Full
    # ------------------------------------

    if system_data["disk_usage"] >= 95:

        incidents.append({

            "severity": "Critical",

            "type": "Disk Capacity",

            "description": "Disk usage exceeded 95%"

        })

    # ------------------------------------
    # Suspicious Processes
    # ------------------------------------

    for process in system_data["running_processes"]:

        name = str(process.get("name", "")).lower()

        if name in SUSPICIOUS_PROCESS_NAMES:

            incidents.append({

                "severity": "Critical",

                "type": "Suspicious Process",

                "description": name

            })

        for keyword in POWERSHELL_KEYWORDS:

            if keyword in name:

                incidents.append({

                    "severity": "Critical",

                    "type": "PowerShell Suspicious",

                    "description": name

                })

    return incidents