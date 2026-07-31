"""Disease and pest symptom matcher for PlantGuide."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

@dataclass
class Symptom:
    name: str
    weight: float = 1.0
    category: str = "general"

@dataclass
class Disease:
    name: str
    symptoms: List[str]
    treatments: List[str]
    severity: str = "medium"  # low, medium, high, critical
    category: str = "disease"  # disease, pest, deficiency
    description: str = ""

# Knowledge base of common plant diseases
DISEASE_KB: List[Disease] = [
    Disease(
        name="Powdery Mildew",
        symptoms=["white powder on leaves", "powdery coating", "leaf distortion", "stunted growth"],
        treatments=["neem oil spray", "baking soda solution", "increase air circulation", "remove affected leaves"],
        severity="medium",
        category="disease",
        description="Fungal disease appearing as white powdery spots on leaves and stems."
    ),
    Disease(
        name="Root Rot",
        symptoms=["wilting", "yellow leaves", "brown mushy roots", "stunted growth", "leaf drop"],
        treatments=["improve drainage", "reduce watering", "fungicide treatment", "repot in fresh soil"],
        severity="high",
        category="disease",
        description="Fungal disease caused by overwatering and poor drainage."
    ),
    Disease(
        name="Aphids",
        symptoms=["sticky residue on leaves", "curled leaves", "yellow spots", "ants on plant", "distorted new growth"],
        treatments=["insecticidal soap", "neem oil", "ladybugs (natural predator)", "strong water spray"],
        severity="medium",
        category="pest",
        description="Small sap-sucking insects that cluster on new growth."
    ),
    Disease(
        name="Spider Mites",
        symptoms=["fine webbing", "tiny dots on leaves", "leaf yellowing", "bronzing", "leaf drop"],
        treatments=["miticide", "neem oil", "increase humidity", "insecticidal soap"],
        severity="medium",
        category="pest",
        description="Tiny arachnids that feed on plant cells, leaving stippling damage."
    ),
    Disease(
        name="Nitrogen Deficiency",
        symptoms=["yellow lower leaves", "pale green color", "stunted growth", "thin stems"],
        treatments=["nitrogen-rich fertilizer", "compost tea", "blood meal", "fish emulsion"],
        severity="low",
        category="deficiency",
        description="Lack of nitrogen causing chlorosis in older leaves first."
    ),
    Disease(
        name="Iron Deficiency",
        symptoms=["yellow new leaves", "green veins", "interveinal chlorosis", "stunted growth"],
        treatments=["iron chelate", "lower soil pH", "iron sulfate", "foliar spray"],
        severity="low",
        category="deficiency",
        description="Iron chlorosis affecting young leaves with green veins."
    ),
    Disease(
        name="Leaf Spot",
        symptoms=["brown spots on leaves", "yellow halos", "leaf drop", "dark lesions"],
        treatments=["copper fungicide", "remove infected leaves", "improve air flow", "avoid overhead watering"],
        severity="medium",
        category="disease",
        description="Bacterial or fungal spots causing necrotic lesions on foliage."
    ),
    Disease(
        name="Mealybugs",
        symptoms=["white cottony masses", "sticky honeydew", "yellow leaves", "sooty mold", "stunted growth"],
        treatments=["rubbing alcohol on cotton swab", "neem oil", "insecticidal soap", "ladybugs"],
        severity="medium",
        category="pest",
        description="Soft-bodied insects covered in white waxy coating."
    ),
    Disease(
        name="Blight",
        symptoms=["rapid wilting", "dark lesions on stems", "leaf browning", "plant collapse", "water-soaked spots"],
        treatments=["copper-based fungicide", "remove infected plants", "crop rotation", "avoid overhead watering"],
        severity="critical",
        category="disease",
        description="Fast-spreading fungal/bacterial disease causing rapid tissue death."
    ),
    Disease(
        name="Scale Insects",
        symptoms=["brown bumps on stems", "sticky honeydew", "yellow leaves", "sooty mold", "weak growth"],
        treatments=["horticultural oil", "neem oil", "manual removal", "prune heavily infested parts"],
        severity="medium",
        category="pest",
        description="Armored insects that attach to stems and leaves, sucking sap."
    ),
]


class SymptomMatcher:
    """Match observed symptoms to known plant diseases."""
    
    def __init__(self, knowledge_base: Optional[List[Disease]] = None):
        self.kb = knowledge_base or DISEASE_KB
    
    def match(self, observed_symptoms: List[str], top_k: int = 3) -> List[Tuple[Disease, float]]:
        """Match observed symptoms against knowledge base.
        
        Args:
            observed_symptoms: List of symptom descriptions from the user
            top_k: Number of top matches to return
            
        Returns:
            List of (Disease, match_score) tuples sorted by descending score
        """
        if not observed_symptoms:
            return []
        
        observed_lower = [s.lower().strip() for s in observed_symptoms]
        scores = []
        
        for disease in self.kb:
            score = self._calculate_score(observed_lower, disease)
            if score > 0:
                scores.append((disease, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def _calculate_score(self, observed: List[str], disease: Disease) -> float:
        """Calculate match score between observed symptoms and a disease."""
        matched = 0
        total_weight = 0
        
        for disease_symptom in disease.symptoms:
            ds_lower = disease_symptom.lower()
            for obs in observed:
                # Check for substring match (handles partial descriptions)
                if ds_lower in obs or obs in ds_lower:
                    matched += 1
                    break
        
        if not disease.symptoms:
            return 0.0
        
        coverage = matched / len(disease.symptoms)
        
        # Severity bonus
        severity_mult = {'low': 0.8, 'medium': 1.0, 'high': 1.2, 'critical': 1.5}
        mult = severity_mult.get(disease.severity, 1.0)
        
        return coverage * mult
    
    def get_care_guide(self, disease_name: str) -> Optional[Dict]:
        """Get treatment and care information for a specific disease."""
        for disease in self.kb:
            if disease.name.lower() == disease_name.lower():
                return {
                    'name': disease.name,
                    'description': disease.description,
                    'category': disease.category,
                    'severity': disease.severity,
                    'treatments': disease.treatments,
                    'prevention': self._get_prevention(disease.category)
                }
        return None
    
    def _get_prevention(self, category: str) -> List[str]:
        """Get prevention tips by category."""
        tips = {
            'disease': [
                'Ensure proper air circulation between plants',
                'Avoid overhead watering to keep foliage dry',
                'Remove and destroy infected plant material',
                'Use disease-resistant plant varieties',
                'Apply preventive fungicide in humid conditions'
            ],
            'pest': [
                'Regularly inspect plants, especially leaf undersides',
                'Introduce beneficial insects (ladybugs, lacewings)',
                'Keep garden area free of weeds and debris',
                'Use companion planting to repel pests',
                'Apply neem oil as preventive treatment'
            ],
            'deficiency': [
                'Test soil pH and nutrient levels regularly',
                'Apply balanced slow-release fertilizer',
                'Add organic compost to improve soil health',
                'Maintain proper watering schedule',
                'Use mulch to retain soil moisture and nutrients'
            ]
        }
        return tips.get(category, ['Maintain regular plant care routine'])
    
    def get_all_categories(self) -> List[str]:
        """Get list of all disease categories in the knowledge base."""
        return sorted(set(d.category for d in self.kb))
    
    def search_by_category(self, category: str) -> List[Disease]:
        """Get all diseases in a specific category."""
        return [d for d in self.kb if d.category.lower() == category.lower()]
