MITRE_ATTACKS = {
    "Brute Force": {
        "technique": "T1110",
        "tactic": "Credential Access"
    },
    "Malware": {
        "technique": "T1204",
        "tactic": "Execution"
    },
    "Ransomware": {
        "technique": "T1486",
        "tactic": "Impact"
    },
    "USB Attack": {
        "technique": "T1091",
        "tactic": "Initial Access"
    },
    "Port Scan": {
        "technique": "T1046",
        "tactic": "Discovery"
    },
    "Privilege Escalation": {
        "technique": "T1068",
        "tactic": "Privilege Escalation"
    },
    "Data Exfiltration": {
        "technique": "T1048",
        "tactic": "Exfiltration"
    },
    "Command & Control": {
        "technique": "T1071",
        "tactic": "Command and Control"
    }
}


def map_attack(attack_type):

    return MITRE_ATTACKS.get(
        attack_type,
        {
            "technique": "Unknown",
            "tactic": "Unknown"
        }
    )