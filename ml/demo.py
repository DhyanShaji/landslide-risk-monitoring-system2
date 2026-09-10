import pandas as pd


# -----------------------------------------
# Load risk data
# -----------------------------------------

file = "data/processed/risk_scores.csv"

df = pd.read_csv(file)


# -----------------------------------------
# Select a high-risk location
# -----------------------------------------

high_risk = df[
    df["Risk_Score"] >= 76
]

location = high_risk.iloc[0]


# -----------------------------------------
# Risk information
# -----------------------------------------

score = location["Risk_Score"]
level = location["Risk_Level"]


# -----------------------------------------
# Display
# -----------------------------------------

print("\n")
print("=" * 50)
print("       AI LANDSLIDE EARLY WARNING SYSTEM")
print("=" * 50)

print("\n📍 LOCATION")
print("-" * 50)

print(
    f"Latitude  : {location['Latitude']}"
)

print(
    f"Longitude : {location['Longitude']}"
)


print("\n🌍 ENVIRONMENTAL CONDITIONS")
print("-" * 50)

print(
    f"Elevation : {location['Elevation']:.2f} m"
)

print(
    f"Slope     : {location['Slope']:.2f}°"
)

print(
    f"Rainfall  : {location['Rainfall_2023']:.2f} mm"
)


print("\n🤖 AI RISK ASSESSMENT")
print("-" * 50)

print(
    f"Risk Score : {score:.2f}/100"
)

print(
    f"Risk Level : {level}"
)


# -----------------------------------------
# Action engine
# -----------------------------------------

print("\n🚨 RECOMMENDED ACTION")
print("-" * 50)


if score >= 76:

    print("⚠️ IMMEDIATE EVACUATION RECOMMENDED")

    print("\nActions:")

    print("• Move away from steep slopes.")

    print("• Avoid landslide-prone roads.")

    print("• Proceed to the safest available shelter.")

    print("• Share your location with emergency responders.")


elif score >= 51:

    print("⚠️ HIGH RISK — STAY ALERT")

    print("\nActions:")

    print("• Avoid unnecessary travel.")

    print("• Monitor rainfall and risk updates.")

    print("• Be prepared to evacuate.")


elif score >= 26:

    print("⚠️ MODERATE RISK")

    print("\nActions:")

    print("• Monitor weather conditions.")

    print("• Avoid unstable slopes.")

    print("• Keep emergency supplies ready.")


else:

    print("✅ LOW RISK")

    print("Continue normal activities.")


print("\n")
print("=" * 50)
print("        END OF RISK ASSESSMENT")
print("=" * 50)