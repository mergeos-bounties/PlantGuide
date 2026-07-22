import unittest
from unittest.mock import patch, mock_open
import argparse
import json
from io import StringIO

from plantguide.cli import list_pet_safe_plants

class TestCLI(unittest.TestCase):
    @patch("plantguide.filters.filter_pet_safe_plants")
    def test_list_pet_safe_plants(self, mock_filter):
        # Setup mock data
        mock_data = [
            {"id": "monstera", "common_name": "Monstera", "scientific_name": "Monstera deliciosa", "toxicity": "none"},
            {"id": "pothos", "common_name": "Pothos", "scientific_name": "Epipremnum aureum", "toxicity": "none"}
        ]
        mock_filter.return_value = mock_data

        # Setup argparse
        parser = argparse.ArgumentParser()
        args = parser.parse_args([])

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            list_pet_safe_plants(args)
            output = fake_out.getvalue().strip()

        # Assert
        self.assertIn("Monstera (Monstera deliciosa) - Toxicity: none", output)
        self.assertIn("Pothos (Epipremnum aureum) - Toxicity: none", output)

if __name__ == "__main__":
    unittest.main()