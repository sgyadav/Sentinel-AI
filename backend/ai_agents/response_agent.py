def generate_response(attack_type):

    if attack_type == "Brute Force":
        return {
            "action": "Block IP Address",
            "priority": "High"
        }

    elif attack_type == "Malware":
        return {
            "action": "Quarantine Device",
            "priority": "Critical"
        }

    elif attack_type == "USB Attack":
        return {
            "action": "Disable USB Port",
            "priority": "Medium"
        }

    elif attack_type == "Reconnaissance":
        return {
            "action": "Enable Firewall Rule",
            "priority": "Medium"
        }

    elif attack_type == "Ransomware":
        return {
            "action": "Disconnect Device and Start Backup Recovery",
            "priority": "Critical"
        }

    return {
        "action": "Continue Monitoring",
        "priority": "Low"
    }