import json
from typing import List, Dict, Optional

class DiseaseMatcher:
    def __init__(self, diseases_file: str = 'data/diseases.json'):
        self.diseases = self._load_diseases(diseases_file)

    def _load_diseases(self, file_path: str) -> List[Dict]:
        with open(file_path, 'r') as f:
            return json.load(f)

    def match_symptoms(self, symptoms: List[str]) -> List[Dict]:
        matched_diseases = []
        for disease in self.diseases:
            if all(symptom in disease['symptoms'] for symptom in symptoms):
                matched_diseases.append({
                    'name': disease['name'],
                    'description': disease['description'],
                    'remedies': disease['remedies'],
                    'disclaimer': disease.get('disclaimer', 'Consult a professional for serious cases.')
                })
        return matched_diseases

    def get_disease_info(self, disease_name: str) -> Optional[Dict]:
        for disease in self.diseases:
            if disease['name'].lower() == disease_name.lower():
                return {
                    'name': disease['name'],
                    'description': disease['description'],
                    'remedies': disease['remedies'],
                    'disclaimer': disease.get('disclaimer', 'Consult a professional for serious cases.')
                }
        return None