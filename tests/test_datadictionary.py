import unittest

from esoreader import DataDictionary


class TestDataDictionary(unittest.TestCase):

    def setUp(self):
        self.dd = DataDictionary(version="9.6.0", timestamp="2025-07-25 22:00:00")
        self.dd.variables = {
            1: ["Hourly", "Zone1", "Zone Air Temperature", "C"],
            2: ["Hourly", "Zone2", "Zone Humidity", "%"],
            3: ["Daily", "Zone1", "Zone Air Temperature", "C"],
        }
        self.dd.build_index()

    def test_metadata_set_correctly(self):
        self.assertEqual(self.dd.version, "9.6.0")
        self.assertEqual(self.dd.timestamp, "2025-07-25 22:00:00")

    def test_index_built_properly(self):
        expected = ("Hourly", "Zone1", "Zone Air Temperature")
        self.assertIn(expected, self.dd.index)
        self.assertEqual(self.dd.index[expected], 1)

    def test_find_variable_case_insensitive(self):
        results = self.dd.find_variable("temperature")
        self.assertEqual(len(results), 2)
        self.assertIn(("Hourly", "Zone1", "Zone Air Temperature"), results)
        self.assertIn(("Daily", "Zone1", "Zone Air Temperature"), results)

    def test_find_variable_partial_match(self):
        results = self.dd.find_variable("humidity")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Zone2")

    def test_find_variable_no_matches(self):
        results = self.dd.find_variable("nonexistent")
        self.assertEqual(results, [])

    def test_build_index_multiple_times(self):
        self.dd.build_index()
        self.dd.build_index()
        expected = ("Hourly", "Zone1", "Zone Air Temperature")
        self.assertIn(expected, self.dd.index)
        self.assertEqual(self.dd.index[expected], 1)

    def test_find_variable_with_empty_search_string(self):
        results = self.dd.find_variable("")
        self.assertEqual(len(results), 3)
