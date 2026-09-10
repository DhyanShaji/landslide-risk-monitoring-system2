import pandas as pd
import math


# -----------------------------------------
# Load shelter data
# -----------------------------------------

shelters = pd.read_csv(
    "data/processed/shelters.csv"
)


# -----------------------------------------
# User location
# -----------------------------------------

user_lat = 26.1900
user_lon = 91.7500


# -----------------------------------------
# Distance calculation
# -----------------------------------------

def calculate_distance(
    lat1, lon1, lat2, lon2
):

    R = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = lat2 - lat1
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# -----------------------------------------
# Calculate shelter distances
# -----------------------------------------

shelters["Distance_km"] = shelters.apply(
    lambda row: calculate_distance(
        user_lat,
        user_lon,
        row["Latitude"],
        row["Longitude"]
    ),
    axis=1
)


# -----------------------------------------
# Rank shelters
# -----------------------------------------

shelters = shelters.sort_values(
    by="Distance_km"
)


# -----------------------------------------
# Display recommendations
# -----------------------------------------

print("\n")
print("=" * 55)
print("       SAFE SHELTER RECOMMENDATION")
print("=" * 55)

print(
    f"\nUser Location: "
    f"{user_lat}, {user_lon}"
)

print("\nNearby shelters:")
print("-" * 55)


for _, shelter in shelters.head(3).iterrows():

    print(
        f"\n🏠 {shelter['Name']}"
    )

    print(
        f"Distance: "
        f"{shelter['Distance_km']:.2f} km"
    )

    print(
        f"Capacity: "
        f"{int(shelter['Capacity'])} people"
    )


# -----------------------------------------
# Safest nearby shelter
# -----------------------------------------

best = shelters.iloc[0]

print("\n")
print("RECOMMENDED SHELTER")
print("-" * 55)

print(
    f"🏠 {best['Name']}"
)

print(
    f"Distance: "
    f"{best['Distance_km']:.2f} km"
)

print(
    f"Capacity: "
    f"{int(best['Capacity'])} people"
)

print(
    "\nProceed to the recommended shelter "
    "using a safe, accessible route."
)

print("=" * 55)