# tests/test_integration.py

import unittest
import json
from src.main import CryptoProcessor

class TestCryptoProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = CryptoProcessor('tests/test_data.json', 'tests/output')

    def test_load_data(self):
        data = self.processor.load_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_process_single_entry(self):
        test_entry = {
            "hex": "48656c6c6f",   # 'Hello'
            "unknown": "SGVsbG8="
        }
        result = self.processor.process_single_entry(test_entry)
        self.assertEqual(result['original_hex'], "48656c6c6f")
        self.assertEqual(result['original_unknown'], "SGVsbG8=")
        self.assertEqual(result['hex_to_ascii'], "Hello")
        self.assertEqual(result['unknown_to_hex'], "48656c6c6f")
        self.assertTrue(result['validation_result'])

    def test_process_all_data(self):
        self.processor.save_results([
            {
                "original_hex": "48656c6c6f",
                "original_unknown": "SGVsbG8=",
                "hex_to_ascii": "Hello",
                "unknown_to_hex": "48656c6c6f",
                "validation_result": True
            }
        ])
        # Check if file exists and is written correctly
        summary_file = 'tests/output/summary_*.json'
        self.assertTrue(any(Path(summary_file).glob()))

if __name__ == '__main__':
    unittest.main()
