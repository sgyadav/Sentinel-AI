from storage import incidents


def ask_ai(question: str):

    question = question.lower()

    if "risk" in question:

        if len(incidents) == 0:

            return {
                "answer": "No incidents available."
            }

        latest = incidents[-1]

        return {

            "answer":
            f"""
Host : {latest['hostname']}

Attack : {latest['attack_type']}

Risk Score : {latest['risk_score']}

Recommendation :

{latest['recommendation']}

Priority :

{latest['priority']}
"""
        }

    return {

        "answer":
        "I couldn't understand your question. refer to the documentation for the available queries."

    }