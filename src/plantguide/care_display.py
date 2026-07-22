# Add this import at the top of the file
from plantguide.disease_matcher import DiseaseMatcher

# Add this function to the CareDisplay class
def show_with_symptoms(self, species_name: str, symptoms: List[str] = None):
    """
    Display care information for a species, optionally including disease matching for symptoms.

    Args:
        species_name: Name of the species to display care for
        symptoms: List of symptom tags to match against diseases
    """
    care_info = self.show(species_name)

    if symptoms:
        matcher = DiseaseMatcher()
        disease_matches = matcher.match_symptoms(symptoms)

        if disease_matches:
            care_info['potential_diseases'] = disease_matches
            care_info['disclaimer'] = "Potential disease matches are suggestions only. For accurate diagnosis, consult a professional."

    return care_info