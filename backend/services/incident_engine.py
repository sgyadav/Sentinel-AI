import uuid
from datetime import datetime


def generate_incidents(agent_data):

    incidents = []

    # High CPU
    if agent_data.cpu_usage > 90:
        incidents.append({
            "incident_id": str(uuid.uuid4()),
            "severity": "High",
            "attack_type": "Resource Abuse",
            "description": f"CPU usage reached {agent_data.cpu_usage}%",
            "recommendation": "Investigate running processes.",
            "risk_score": 75,
            "created_at": str(datetime.utcnow())
        })

    # High RAM
    if agent_data.ram_usage > 90:
        incidents.append({
            "incident_id": str(uuid.uuid4()),
            "severity": "Medium",
            "attack_type": "Memory Abuse",
            "description": f"RAM usage reached {agent_data.ram_usage}%",
            "recommendation": "Check for memory leaks or suspicious software.",
            "risk_score": 60,
            "created_at": str(datetime.utcnow())
        })

    # Suspicious process names
    suspicious = [
        "mimikatz.exe",
        "nc.exe",
        "netcat.exe",
        "psexec.exe"
    ]

    for process in agent_data.running_processes:

        name = str(process.get("name", "")).lower()

        if name in suspicious:

            incidents.append({
                "incident_id": str(uuid.uuid4()),
                "severity": "Critical",
                "attack_type": "Credential Attack",
                "description": f"{name} detected",
                "recommendation": "Isolate endpoint immediately.",
                "risk_score": 98,
                "created_at": str(datetime.utcnow())
            })

    return incidents