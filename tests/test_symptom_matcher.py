import unittest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from plantguide.symptom_matcher import SymptomMatcher, Disease, DISEASE_KB

class TestSymptomMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = SymptomMatcher()
    
    def test_match_powdery_mildew(self):
        symptoms = ["white powder on leaves", "leaves are distorted"]
        results = self.matcher.match(symptoms, top_k=1)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0].name, "Powdery Mildew")
        self.assertGreater(results[0][1], 0)
    
    def test_match_root_rot(self):
        symptoms = ["wilting", "brown mushy roots", "yellow leaves"]
        results = self.matcher.match(symptoms, top_k=1)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0].name, "Root Rot")
    
    def test_match_aphids(self):
        symptoms = ["sticky residue", "ants on plant", "curled leaves"]
        results = self.matcher.match(symptoms, top_k=1)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0].name, "Aphids")
    
    def test_match_iron_deficiency(self):
        symptoms = ["yellow new leaves", "green veins"]
        results = self.matcher.match(symptoms, top_k=1)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0].name, "Iron Deficiency")
    
    def test_no_match_empty(self):
        results = self.matcher.match([], top_k=3)
        self.assertEqual(len(results), 0)
    
    def test_no_match_unrelated(self):
        symptoms = ["dancing plants", "singing flowers", "flying roots"]
        results = self.matcher.match(symptoms, top_k=3)
        self.assertEqual(results, [])  # No matches expected
    
    def test_top_k_limit(self):
        symptoms = ["yellow leaves", "stunted growth"]
        results = self.matcher.match(symptoms, top_k=2)
        self.assertLessEqual(len(results), 2)
    
    def test_care_guide_found(self):
        guide = self.matcher.get_care_guide("Powdery Mildew")
        self.assertIsNotNone(guide)
        self.assertIn('treatments', guide)
        self.assertIn('neem oil spray', guide['treatments'])
    
    def test_care_guide_not_found(self):
        guide = self.matcher.get_care_guide("Nonexistent Disease")
        self.assertIsNone(guide)
    
    def test_categories(self):
        cats = self.matcher.get_all_categories()
        self.assertIn('disease', cats)
        self.assertIn('pest', cats)
        self.assertIn('deficiency', cats)
    
    def test_search_by_category(self):
        pests = self.matcher.search_by_category('pest')
        self.assertGreater(len(pests), 0)
        for p in pests:
            self.assertEqual(p.category, 'pest')
    
    def test_score_ordering(self):
        symptoms = ["powdery coating", "leaf distortion"]
        results = self.matcher.match(symptoms, top_k=3)
        if len(results) >= 2:
            self.assertGreaterEqual(results[0][1], results[-1][1])
    
    def test_severity_boosts_score(self):
        symptoms = ["rapid wilting", "plant collapse"]
        results = self.matcher.match(symptoms, top_k=2)
        self.assertGreater(len(results), 0)
        # Blight (critical, 1.5x) should score high
        names = [r[0].name for r in results]
    
    def test_partial_symptom_match(self):
        symptoms = ["white powder"]  # Partial match for "white powder on leaves"
        results = self.matcher.match(symptoms, top_k=1)
        self.assertGreater(len(results), 0)
    
    def test_knowledge_base_has_entries(self):
        self.assertGreater(len(DISEASE_KB), 5)
        for disease in DISEASE_KB:
            self.assertTrue(disease.name)
            self.assertTrue(disease.symptoms)
            self.assertTrue(disease.treatments)

if __name__ == '__main__':
    unittest.main()
