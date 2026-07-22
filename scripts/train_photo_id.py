import argparse
import os
import json
from typing import List, Dict
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import joblib
from plantguide.ai.species import Species

def load_species_data(species_data_path: str) -> List[Species]:
    """Load species data from JSON files."""
    species = []
    for filename in os.listdir(species_data_path):
        if filename.endswith(".json"):
            with open(os.path.join(species_data_path, filename), "r") as f:
                species_data = json.load(f)
                species.append(Species(**species_data))
    return species

def prepare_dataset(species: List[Species]) -> tuple:
    """Prepare dataset for training."""
    X = []
    y = []

    for species_data in species:
        # Use color features as a placeholder
        # In a real implementation, this would use more sophisticated features
        X.append(species_data.color_features["histogram"])
        y.append(species_data.scientific_name)

    return np.array(X), np.array(y)

def train_model(X_train: np.ndarray, y_train: np.ndarray) -> SVC:
    """Train a classifier model."""
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_train)

    # Train a simple SVM classifier
    # In a real implementation, this would use a more sophisticated model
    model = SVC(kernel='linear', probability=True)
    model.fit(X_train, y_encoded)

    return model, label_encoder

def evaluate_model(model: SVC, X_test: np.ndarray, y_test: np.ndarray, label_encoder: LabelEncoder) -> None:
    """Evaluate the trained model."""
    y_pred = model.predict(X_test)
    print(classification_report(y_test, label_encoder.inverse_transform(y_pred)))

def main():
    parser = argparse.ArgumentParser(description="Train photo identification model")
    parser.add_argument("--species-data", type=str, default="data/species",
                        help="Path to species data directory")
    parser.add_argument("--output", type=str, default="models/photo_id_model.pkl",
                        help="Path to save the trained model")
    args = parser.parse_args()

    # Load and prepare data
    species = load_species_data(args.species_data)
    X, y = prepare_dataset(species)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model, label_encoder = train_model(X_train, y_train)

    # Evaluate model
    evaluate_model(model, X_test, y_test, label_encoder)

    # Save model
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    joblib.dump((model, label_encoder), args.output)
    print(f"Model saved to {args.output}")

if __name__ == "__main__":
    main()