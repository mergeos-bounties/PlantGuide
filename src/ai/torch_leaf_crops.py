import os
from typing import Optional, Dict, List
import numpy as np
from PIL import Image
import torch
from torch import nn
from torchvision import transforms

class LeafCropClassifier:
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_path)
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def _load_model(self, model_path: Optional[str]) -> Optional[nn.Module]:
        """Load a pre-trained model if available."""
        if model_path and os.path.exists(model_path):
            try:
                model = torch.load(model_path, map_location=self.device)
                model.eval()
                return model
            except Exception as e:
                print(f"Error loading model: {str(e)}")
                return None
        return None

    def classify(self, image_path: str) -> Optional[Dict]:
        """Classify a leaf crop image."""
        if not self.model:
            print("PyTorch model not available. Skipping classification.")
            return None

        try:
            image = Image.open(image_path).convert("RGB")
            image = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(image)
                _, predicted = torch.max(outputs, 1)

            # In a real implementation, this would map to species names
            return {"class_id": predicted.item(), "confidence": outputs.max().item()}

        except Exception as e:
            print(f"Error classifying image: {str(e)}")
            return None