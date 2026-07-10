def analyze_event(event_type):

    if event_type == "Failed Login":
        return {
            "alert": "Possible Brute Force Attack",
            "risk_score": 85,
            "attack_type": "Brute Force"
        }

    return {
        "alert": None,
        "risk_score": 20,
        "attack_type": "Unknown"
    }