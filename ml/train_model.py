import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import joblib


# -----------------------------------------
# File paths
# -----------------------------------------

input_file = "data/processed/ml_training_dataset.csv"

model_file = "data/processed/landslide_random_forest.pkl"


# -----------------------------------------
# Load dataset
# -----------------------------------------

df = pd.read_csv(input_file)

print("Dataset loaded!")
print("Total samples:", len(df))


# -----------------------------------------
# Select features
# -----------------------------------------

features = [
    "Elevation",
    "Slope",
    "Rainfall_2023"
]

X = df[features]

y = df["Label"]


# -----------------------------------------
# Split dataset
# -----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# -----------------------------------------
# Create Random Forest
# -----------------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)


# -----------------------------------------
# Train model
# -----------------------------------------

print("\nTraining Random Forest...")

model.fit(X_train, y_train)

print("Training completed!")


# -----------------------------------------
# Predictions
# -----------------------------------------

y_pred = model.predict(X_test)


# -----------------------------------------
# Accuracy
# -----------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\nModel Accuracy:")
print(f"{accuracy * 100:.2f}%")


# -----------------------------------------
# Classification report
# -----------------------------------------

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)


# -----------------------------------------
# Confusion matrix
# -----------------------------------------

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# -----------------------------------------
# Feature importance
# -----------------------------------------

print("\nFeature Importance:")

for feature, importance in zip(
    features,
    model.feature_importances_
):

    print(
        f"{feature}: {importance:.4f}"
    )


# -----------------------------------------
# Save model
# -----------------------------------------

joblib.dump(
    model,
    model_file
)

print("\nModel saved to:")

print(model_file)