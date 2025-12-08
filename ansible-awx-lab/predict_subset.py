#!/usr/bin/env python3

import pandas as pd
import numpy as np
import joblib
import argparse

# --- Arguments for flexibility ---
parser = argparse.ArgumentParser(description="Predict flood/normal packets from a CSV using a trained Random Forest.")
parser.add_argument("--csv", type=str, default="data/network_traffic_normal_heavy.csv", help="Input CSV file")
parser.add_argument("--model", type=str, default="rf_flood_model.pkl", help="Trained RF model file")
parser.add_argument("--n_packets", type=int, default=1300, help="Number of packets to predict in subset")
parser.add_argument("--normal_ratio", type=float, default=0.77, help="Ratio of normal packets in subset (0-1)")
args = parser.parse_args()

# --- Load dataset ---
df = pd.read_csv(args.csv)

# --- Load trained model ---
model = joblib.load(args.model)

# --- Determine subset counts ---
n_normal = int(args.n_packets * args.normal_ratio)
n_flood = args.n_packets - n_normal

# --- Sample subset ---
normal_samples = df[df["bad_packet"] == 0].sample(n=n_normal, random_state=42)
flood_samples = df[df["bad_packet"] == 1].sample(n=n_flood, random_state=42)
subset = pd.concat([normal_samples, flood_samples]).sample(frac=1, random_state=42)

# --- Prepare features ---
features = ["Source Port", "Destination Port", "Protocol", "Length"]
X_subset = pd.get_dummies(subset[features], columns=["Protocol"])

# --- Align columns to trained model ---
missing_cols = set(model.feature_names_in_) - set(X_subset.columns)
for c in missing_cols:
    X_subset[c] = 0
X_subset = X_subset[model.feature_names_in_]

# --- Make predictions ---
predictions = model.predict(X_subset)

# --- Subset summary ---
true_labels = subset["bad_packet"].values
accuracy = (predictions == true_labels).mean() * 100
result_counts = {"FLOOD_DETECTED": int((predictions==1).sum()), "NORMAL": int((predictions==0).sum())}

print("\n--- Subset Prediction Summary ---")
print(f"Total packets: {len(subset)}")
print(f"FLOOD_DETECTED: {result_counts['FLOOD_DETECTED']}")
print(f"NORMAL: {result_counts['NORMAL']}")
print(f"Accuracy on this subset: {accuracy:.2f}%")

# Optional: show first 10 predictions
print("\nSample predictions:")
for i, p in enumerate(predictions[:10], 1):
    status = "FLOOD_DETECTED" if p == 1 else "NORMAL"
    print(f"Packet {i}: {status}")
