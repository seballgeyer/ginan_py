"""
Unittest file for patterns
@author Sebastien Allgeyer
@date 2023-03-10
"""
import unittest

from sateda.utils.patterns import match_patterns


class TestPattern(unittest.TestCase):
    """
    Class testing pattern
    """

    def test_match1wildcard(self) -> None:
        """
        test matching pattern
        Given a list of values and a pattern, find the values that match the pattern
        :return:
        """
        list_val = ["G01", "G02", "G03", "E01", "E02"]
        pattern = ["*1"]
        matched_values = [value for value in list_val if match_patterns(pattern, value)]
        self.assertEqual(len(matched_values), 2)  # add assertion here
        self.assertListEqual(matched_values, ["G01", "E01"])

    def test_match1questionmark(self) -> None:
        """
        test matching pattern question mark
        Given a list of values and a pattern, find the values that match the pattern
        :return:
        """
        list_val = ["G01", "G02", "G03", "E01", "E02"]
        pattern = ["G0?"]
        matched_values = [value for value in list_val if match_patterns(pattern, value)]
        self.assertEqual(len(matched_values), 3)  # add assertion here
        self.assertListEqual(matched_values, ["G01", "G02", "G03"])

    def test_match2questionmark(self) -> None:
        """
        test matching pattern 2 question mark
        Given a list of values and a pattern, find the values that match the pattern
        :return:
        """
        list_val = ["G01", "G02", "G03", "G25", "E01", "E02", "E14"]
        pattern = ["?0?"]
        matched_values = [value for value in list_val if match_patterns(pattern, value)]
        self.assertEqual(len(matched_values), 5)  # add assertion here
        self.assertListEqual(matched_values, ["G01", "G02", "G03", "E01", "E02"])


if __name__ == "__main__":
    unittest.main()
