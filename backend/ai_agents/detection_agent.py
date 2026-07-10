def analyze_event(event_type):

    if event_type == "Failed Login":
        return {
            "alert": "Possible Brute Force Attack",
            "attack_type": "Brute Force",
            "risk_score": 90
        }

    elif event_type == "Malware":
        return {
            "alert": "Malware Detected",
            "attack_type": "Malware",
            "risk_score": 95
        }

    elif event_type == "USB Connected":
        return {
            "alert": "Unauthorized USB Device",
            "attack_type": "USB Attack",
            "risk_score": 70
        }

    elif event_type == "Port Scan":
        return {
            "alert": "Network Port Scan",
            "attack_type": "Reconnaissance",
            "risk_score": 80
        }

    elif event_type == "Ransomware":
        return {
            "alert": "Possible Ransomware Activity",
            "attack_type": "Ransomware",
            "risk_score": 100
        }

    else:
        return {
            "alert": "Unknown Activity",
            "attack_type": "Unknown",
            "risk_score": 20
        }