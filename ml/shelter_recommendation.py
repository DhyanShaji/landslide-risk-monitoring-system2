import pandas as pd
import numpy as np


# =========================================
# FILE PATHS
# =========================================

shelter_file = "data/processed/shelters.csv"
risk_file = "data/processed/risk_scores.csv"


# =========================================
# LOAD DATA
# =========================================

shelters = pd.read_csv(shelter_file)
risk_data = pd.read_csv(risk_file)

print("Shelters loaded:", len(shelters))
print("Risk locations loaded:", len(risk_data))


# =========================================
# USER LOCATION
# =========================================

user_lat = 26.1900
user_lon = 91.7500


# =========================================
# DISTANCE FUNCTION
# =========================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371.0

    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)

    dlat = lat2 - lat1
    dlon = np.radians(lon2 - lon1)

    a = (
        np.sin(dlat / 2) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arctan2(
        np.sqrt(a),
        np.sqrt(1 - a)
    )

    return R * c


# =========================================
# CALCULATE SHELTER DISTANCE
# =========================================

shelters["Distance_km"] = calculate_distance(
    user_lat,
    user_lon,
    shelters["Latitude"].values,
    shelters["Longitude"].values
)


# =========================================
# ESTIMATE RISK AROUND EACH SHELTER
# =========================================

def estimate_shelter_risk(
    shelter_lat,
    shelter_lon
):

    distances = calculate_distance(
        shelter_lat,
        shelter_lon,
        risk_data["Latitude"].values,
        risk_data["Longitude"].values
    )

    # Take 10 nearest risk locations
    nearest_indices = np.argsort(
        distances
    )[:10]

    nearest_risks = risk_data.iloc[
        nearest_indices
    ]["Risk_Score"]

    return nearest_risks.mean()


shelters["Nearby_Risk"] = shelters.apply(
    lambda row: estimate_shelter_risk(
        row["Latitude"],
        row["Longitude"]
    ),
    axis=1
)


# =========================================
# REMOVE CRITICAL SHELTERS
# =========================================

safe_shelters = shelters[
    shelters["Nearby_Risk"] < 76
].copy()


# =========================================
# SAFETY SCORE
# =========================================

if len(safe_shelters) > 0:

    # Risk safety score
    safe_shelters["Risk_Safety"] = (
        100 - safe_shelters["Nearby_Risk"]
    )

    # Distance score
    max_distance = 20

    safe_shelters["Distance_Score"] = (
        100
        * (
            1
            - (
                safe_shelters["Distance_km"]
                / max_distance
            ).clip(upper=1)
        )
    )

    # Capacity score
    max_capacity = shelters["Capacity"].max()

    safe_shelters["Capacity_Score"] = (
        safe_shelters["Capacity"]
        / max_capacity
        * 100
    )

    # Final safety score
    safe_shelters["Safety_Score"] = (
        0.50
        * safe_shelters["Risk_Safety"]
        +
        0.30
        * safe_shelters["Distance_Score"]
        +
        0.20
        * safe_shelters["Capacity_Score"]
    )

    # Sort by best safety score
    safe_shelters = safe_shelters.sort_values(
        by="Safety_Score",
        ascending=False
    )


# =========================================
# DISPLAY RESULTS
# =========================================

print("\n")
print("=" * 65)
print("       AI SAFE SHELTER RECOMMENDATION")
print("=" * 65)

print(
    f"\nUser Location:"
    f" {user_lat}, {user_lon}"
)


if len(safe_shelters) == 0:

    print("\n⚠️ NO SAFE SHELTER FOUND")

    print(
        "All nearby shelters have high or critical risk."
    )

else:

    print("\nRecommended Shelters:")
    print("-" * 65)

    for _, shelter in safe_shelters.head(5).iterrows():

        print(
            f"\n🏠 {shelter['Name']}"
        )

        print(
            f"Distance       : "
            f"{shelter['Distance_km']:.2f} km"
        )

        print(
            f"Nearby Risk    : "
            f"{shelter['Nearby_Risk']:.2f}/100"
        )

        print(
            f"Capacity       : "
            f"{int(shelter['Capacity'])} people"
        )

        print(
            f"Safety Score   : "
            f"{shelter['Safety_Score']:.2f}/100"
        )


    # =====================================
    # BEST SHELTER
    # =====================================

    best = safe_shelters.iloc[0]

    print("\n")
    print("=" * 65)
    print("              RECOMMENDED SHELTER")
    print("=" * 65)

    print(
        f"\n🏠 {best['Name']}"
    )

    print(
        f"Distance       : "
        f"{best['Distance_km']:.2f} km"
    )

    print(
        f"Nearby Risk    : "
        f"{best['Nearby_Risk']:.2f}/100"
    )

    print(
        f"Capacity       : "
        f"{int(best['Capacity'])} people"
    )

    print(
        f"Safety Score   : "
        f"{best['Safety_Score']:.2f}/100"
    )

    print(
        "\n✅ Recommended because it provides "
        "the best balance of safety, distance "
        "and capacity."
    )

    print(
        "\nProceed using a safe and accessible route."
    )

    print("=" * 65)