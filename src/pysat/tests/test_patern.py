import unittest

from pysat.utils.patterns import match_patterns


class TestPatern(unittest.TestCase):
    def test_match1(self):
        list_val = ["G01", "G02", "G03", "E01", "E02"]
        pattern = ["*1"]
        matched_values = [value for value in list_val if match_patterns(pattern, value)]
        print(matched_values)
        self.assertEqual(True, False)  # add assertion here


if __name__ == "__main__":
    unittest.main()
