import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("ml_training/data/processed/features_dataset.csv")

print(f"Total samples: {len(df)}")
print(f"Features: {df.columns.tolist()}")

# Separate features (X) from labels (y)
X = df.drop("outcome", axis=1)
y = df["outcome"]

print(f"\nFeature matrix shape: {X.shape}")
print(f"Label vector shape: {y.shape}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples")

# Scale features
print("\nScaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Scaled training data shape: {X_train_scaled.shape}")

# Train Random Forest
print("\nTraining Random Forest model...")
model = RandomForestClassifier(
    n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
)

model.fit(X_train_scaled, y_train)
print("Training complete!")

# Evaluate on test set
print("\nEvaluating on test set...")
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nTest Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Feature importance
print("\nFeature Importances:")
feature_names = X.columns.tolist()
importances = model.feature_importances_
for name, importance in sorted(
    zip(feature_names, importances), key=lambda x: x[1], reverse=True
):
    print(f"  {name}: {importance:.4f}")

# Save model and scaler
print("\nSaving model and scaler...")
with open("ml_training/models/soccer_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("ml_training/models/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

print("\nModel saved to ml_training/models/soccer_model.pkl")
print("Scaler saved to ml_training/models/scaler.pkl")
print("\nTraining complete!")
