def get_action(risk_score):

    if risk_score >= 76:

        return {
            "level": "CRITICAL",
            "message": "Immediate evacuation recommended.",
            "actions": [
                "Move away from steep slopes.",
                "Avoid landslide-prone roads.",
                "Proceed to the safest available shelter.",
                "Share your location with emergency responders."
            ]
        }

    elif risk_score >= 51:

        return {
            "level": "HIGH",
            "message": "High landslide risk detected.",
            "actions": [
                "Stay alert for warning signs.",
                "Avoid unnecessary travel.",
                "Monitor rainfall and risk updates.",
                "Be prepared to evacuate."
            ]
        }

    elif risk_score >= 26:

        return {
            "level": "MODERATE",
            "message": "Moderate landslide risk.",
            "actions": [
                "Monitor weather conditions.",
                "Avoid unstable slopes.",
                "Keep emergency supplies ready."
            ]
        }

    else:

        return {
            "level": "LOW",
            "message": "Low landslide risk.",
            "actions": [
                "Continue normal activities.",
                "Monitor weather updates."
            ]
        }


# -----------------------------------------
# Test the action engine
# -----------------------------------------

risk_score = 90

result = get_action(risk_score)

print("\nLANDSLIDE ALERT")
print("------------------------")

print("Risk Score:", risk_score)
print("Risk Level:", result["level"])
print("Message:", result["message"])

print("\nRecommended Actions:")

for action in result["actions"]:
    print("•", action)