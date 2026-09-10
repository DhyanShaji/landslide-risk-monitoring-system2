import pandas as pd


# -----------------------------------------
# File paths
# -----------------------------------------

landslide_file = "data/processed/landslide_features_rainfall.csv"
background_file = "data/processed/background_features.csv"

output_file = "data/processed/ml_training_dataset.csv"


# -----------------------------------------
# Load datasets
# -----------------------------------------

landslides = pd.read_csv(landslide_file)
background = pd.read_csv(background_file)

print("Landslide samples:", len(landslides))
print("Background samples:", len(background))


# -----------------------------------------
# Add labels
# -----------------------------------------

landslides["Label"] = 1

background["Label"] = 0


# -----------------------------------------
# Select ML features
# -----------------------------------------

features = [
    "Latitude",
    "Longitude",
    "Elevation",
    "Slope",
    "Rainfall_2023",
    "Label"
]

landslides = landslides[features]
background = background[features]


# -----------------------------------------
# Combine datasets
# -----------------------------------------

dataset = pd.concat(
    [landslides, background],
    ignore_index=True
)


# -----------------------------------------
# Shuffle dataset
# -----------------------------------------

dataset = dataset.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# -----------------------------------------
# Check missing values
# -----------------------------------------

print("\nMissing values:")

print(dataset.isnull().sum())


# -----------------------------------------
# Save dataset
# -----------------------------------------

dataset.to_csv(
    output_file,
    index=False
)


# -----------------------------------------
# Results
# -----------------------------------------

print("\nTraining dataset created!")

print("Total samples:", len(dataset))

print("\nLabel distribution:")

print(dataset["Label"].value_counts())

print("\nSample:")

print(dataset.head())

print("\nSaved to:")

print(output_file)