"""
Unit testing for YAML input file. 
@author sebastien Allgeyer
@date 2023/03/01

"""
import unittest
import yaml

FILEDATA = """
---
# This is a YAML file
software: "nananana"
date: 2020-01-01T22:30:00
---
2010-01-01T00:00:10:
  objectA:
    posvel: [1, 2, 3, 4, 5, 6]
  objectB:
    posvel: [7, 8, 9, 10, 11, 12]
2010-01-01T00:00:20:
  objectA:
    posvel: [13, 14, 15, 16, 17, 18]
  objectB:
    posvel: [19, 20, 21, 22, 23, 24]
2010-01-01T00:00:30:
  objectA:
    posvel: [13, 14, 15, 16, 17, 18]
  objectB:
    posvel: [19, 20, 21, 22, 23, 24]
2010-01-01T00:00:40:
  objectA:
    posvel: [13, 14, 15, 16, 17, 18]
  objectB:
    posvel: [19, 20, 21, 22, 23, 24]
"""

FILEDATA2 = """
- { time: 2010-01-01T00:00:30, sat: K01, pvECI: [6609647.6819071816, 0, 0, 0, -135.59762707258645, 7768.3828522105196]}
- { time: 2010-01-01T00:00:40, sat: K01, pvECI: [6609647.68190716,   0, 0, 0, -135.59762707258,    7768.3828522105196]}
"""


class TestYAML(unittest.TestCase):
    """
    Unit testing case for YAML
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = yaml.safe_load_all(FILEDATA)
        cls.data2 = yaml.safe_load_all(FILEDATA2)

    def test_something(self):
        """
        Basic test to check yaml file
        :return:
        """
        for line in self.data:
            print(line)
        for line in self.data2:
            print(line)
        self.assertEqual(True, True)  # add assertion here


if __name__ == "__main__":
    unittest.main()
