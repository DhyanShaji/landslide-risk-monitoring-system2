import pandas as pd
import joblib


# -----------------------------------------
# File paths
# -----------------------------------------

input_file = "data/processed/ml_training_dataset.csv"

model_file = "data/processed/landslide_random_forest.pkl"

output_file = "data/processed/risk_scores.csv"


# -----------------------------------------
# Load dataset
# -----------------------------------------

df = pd.read_csv(input_file)

print("Records loaded:", len(df))


# -----------------------------------------
# Load trained model
# -----------------------------------------

model = joblib.load(model_file)

print("Random Forest model loaded.")


# -----------------------------------------
# Select model features
# -----------------------------------------

features = [
    "Elevation",
    "Slope",
    "Rainfall_2023"
]

X = df[features]


# -----------------------------------------
# Get landslide probability
# -----------------------------------------

probability = model.predict_proba(X)[:, 1]


# -----------------------------------------
# Convert to 0–100 risk score
# -----------------------------------------

df["Risk_Score"] = probability * 100


# -----------------------------------------
# Assign risk level
# -----------------------------------------

def get_risk_level(score):

    if score <= 25:
        return "Low"

    elif score <= 50:
        return "Moderate"

    elif score <= 75:
        return "High"

    else:
        return "Critical"


df["Risk_Level"] = df["Risk_Score"].apply(
    get_risk_level
)


# -----------------------------------------
# Round risk score
# -----------------------------------------

df["Risk_Score"] = df["Risk_Score"].round(2)


# -----------------------------------------
# Save
# -----------------------------------------

df.to_csv(
    output_file,
    index=False
)


# -----------------------------------------
# Display results
# -----------------------------------------

print("\nRisk scoring completed!")

print("\nRisk level distribution:")

print(
    df["Risk_Level"].value_counts()
)

print("\nSample:")

print(
    df[
        [
            "Latitude",
            "Longitude",
            "Elevation",
            "Slope",
            "Rainfall_2023",
            "Risk_Score",
            "Risk_Level"
        ]
    ].head(10)
)

print("\nSaved to:")

print(output_file)