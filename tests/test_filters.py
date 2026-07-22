import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import json

from plantguide.filters import load_species_data, filter_pet_safe_plants

class TestFilters(unittest.TestCase):
    @patch("pathlib.Path.glob")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_species_data(self, mock_file, mock_glob):
        # Setup mock data
        mock_glob.return_value = [Path("monstera.json"), Path("snake_plant.json")]
        mock_data = [
            {"id": "monstera", "common_name": "Monstera", "toxicity": "none"},
            {"id": "snake_plant", "common_name": "Snake Plant", "toxicity": "low"}
        ]
        mock_file.return_value.read.return_value = json.dumps(mock_data[0])

        # Test
        result = load_species_data()

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "monstera")

    def test_filter_pet_safe_plants(self):
        # Setup mock data
        mock_data = [
            {"id": "monstera", "common_name": "Monstera", "toxicity": "none"},
            {"id": "snake_plant", "common_name": "Snake Plant", "toxicity": "low"},
            {"id": "pothos", "common_name": "Pothos", "toxicity": "none"}
        ]

        # Patch the load_species_data function
        with patch("plantguide.filters.load_species_data", return_value=mock_data):
            # Test
            result = filter_pet_safe_plants()

            # Assert
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["id"], "monstera")
            self.assertEqual(result[1]["id"], "pothos")

if __name__ == "__main__":
    unittest.main()