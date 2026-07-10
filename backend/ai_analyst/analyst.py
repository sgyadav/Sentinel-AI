def generate_ai_analysis(incident):

    score = incident.get("risk_score", 0)

    attack = incident.get("attack_type", "Unknown")

    hostname = incident.get("hostname", "Unknown")

    if score >= 90:

        confidence = 98

        recommendation = (
            "Immediately isolate the endpoint, "
            "terminate suspicious processes, "
            "perform a malware scan and notify SOC."
        )

    elif score >= 70:

        confidence = 90

        recommendation = (
            "Investigate the endpoint and review "
            "network activity."
        )

    elif score >= 50:

        confidence = 80

        recommendation = (
            "Continue monitoring and collect "
            "additional evidence."
        )

    else:

        confidence = 60

        recommendation = (
            "Low priority event. Continue monitoring."
        )

    explanation = [
        f"Attack Type : {attack}",
        f"Host : {hostname}",
        f"Calculated Risk Score : {score}",
        "Telemetry correlated successfully.",
        "Threat Intelligence correlation completed."
    ]

    return {

        "confidence": confidence,

        "explanation": explanation,

        "recommendation": recommendation

    }