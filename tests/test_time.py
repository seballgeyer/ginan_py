import unittest

from sateda.core.time import Time

class TestTime(unittest.TestCase):
    def setUp(self) -> None:
        self.time = Time.from_components(2007,1,1,0,0,0,0)
    def test_something(self):
        print()
        print(self.time)
        print(self.time.to_utc())
        print(self.time.to_tt())
        print(self.time.to_tai())
        print(self.time.to_utc().to_mjd())
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
