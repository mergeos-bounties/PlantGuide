import os
import json
from typing import List, Dict, Optional
from PIL import Image
import numpy as np
from .species import Species
from .image_processing import preprocess_image

class PhotoIdentifier:
    def __init__(self, species_data_path: str = "data/species"):
        self.species_data_path = species_data_path
        self.species = self._load_species_data()

    def _load_species_data(self) -> List[Species]:
        """Load species data from JSON files."""
        species = []
        for filename in os.listdir(self.species_data_path):
            if filename.endswith(".json"):
                with open(os.path.join(self.species_data_path, filename), "r") as f:
                    species_data = json.load(f)
                    species.append(Species(**species_data))
        return species

    def identify(self, image_path: str, k: int = 3) -> List[Dict]:
        """Identify plant species from an image."""
        try:
            # Preprocess the image
            image = Image.open(image_path)
            processed_image = preprocess_image(image)

            # For demo purposes, we'll use a simple color-based matching
            # In a real implementation, this would use a trained model
            image_colors = self._extract_colors(processed_image)
            matches = []

            for species in self.species:
                # Calculate similarity based on color features
                similarity = self._calculate_similarity(image_colors, species.color_features)
                matches.append({
                    "species": species.scientific_name,
                    "common_name": species.common_name,
                    "similarity": similarity,
                    "care": species.care
                })

            # Sort by similarity and return top k matches
            matches.sort(key=lambda x: x["similarity"], reverse=True)
            return matches[:k]

        except Exception as e:
            raise RuntimeError(f"Error identifying plant: {str(e)}")

    def _extract_colors(self, image: np.ndarray) -> Dict:
        """Extract color features from an image."""
        # Simple color histogram as a placeholder
        # In a real implementation, this would use more sophisticated features
        hist = np.histogramdd(image.reshape(-1, 3), bins=8, range=[(0, 255), (0, 255), (0, 255)])
        return {"histogram": hist[0].flatten()}

    def _calculate_similarity(self, image_features: Dict, species_features: Dict) -> float:
        """Calculate similarity between image and species features."""
        # Simple cosine similarity as a placeholder
        # In a real implementation, this would use more sophisticated metrics
        hist1 = image_features["histogram"]
        hist2 = species_features["histogram"]
        dot_product = np.dot(hist1, hist2)
        norm1 = np.linalg.norm(hist1)
        norm2 = np.linalg.norm(hist2)
        return dot_product / (norm1 * norm2) if (norm1 * norm2) != 0 else 0.0