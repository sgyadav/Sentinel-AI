def decide_response(incident):

    score = incident.get("risk_score", 0)

    attack = incident.get("attack_type", "")

    actions = []

    if score >= 90:

        actions.append("Isolate Endpoint")

        actions.append("Kill Malicious Process")

        actions.append("Block IP")

        actions.append("Notify Administrator")

    elif score >= 70:

        actions.append("Block IP")

        actions.append("Notify Administrator")

    elif score >= 50:

        actions.append("Increase Monitoring")

    else:

        actions.append("No Immediate Action")

    return {

        "attack": attack,

        "risk_score": score,

        "actions": actions

    }