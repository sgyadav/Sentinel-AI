def investigate_attack(attack_type):

    if attack_type == "Brute Force":
        return {
            "confidence": "High",
            "recommendation": "Lock the account and investigate login attempts."
        }

    elif attack_type == "Malware":
        return {
            "confidence": "Critical",
            "recommendation": "Isolate the infected device immediately."
        }

    elif attack_type == "USB Attack":
        return {
            "confidence": "Medium",
            "recommendation": "Verify whether the USB device is authorized."
        }

    elif attack_type == "Reconnaissance":
        return {
            "confidence": "Medium",
            "recommendation": "Block the scanning IP and monitor traffic."
        }

    elif attack_type == "Ransomware":
        return {
            "confidence": "Critical",
            "recommendation": "Disconnect the device from the network immediately."
        }

    return {
        "confidence": "Low",
        "recommendation": "Continue monitoring the system."
    }