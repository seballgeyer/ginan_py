import unittest

from pysat.utils.common import find_common


class MyClass:
    def __init__(self, id, other_attribute):
        self.measurement_id = id
        self.other_attribute = other_attribute


class Testcommon(unittest.TestCase):
    """
    Class testing pattern
    """

    def test_common(self) -> None:
        # Sample data
        a = [
            MyClass({"id1": "value1"}, "attribute1"),
            MyClass({"id2": "value2"}, "attribute2"),
            MyClass({"id3": "value3"}, "attribute3"),
        ]

        b = [
            MyClass({"id2": "value2"}, "attribute4"),
            MyClass({"id3": "value3"}, "attribute5"),
            MyClass({"id4": "value4"}, "attribute6"),
        ]

        common, not_in_b, not_in_a = find_common(a, b)
        self.assertEqual(len(common), 2)  # add assertion here
        self.assertEqual(len(not_in_b), 1)  # add assertion here
        self.assertEqual(len(not_in_a), 1)  # add assertion here
        self.assertListEqual(common, [(1, 0), (2, 1)])
        self.assertListEqual(not_in_b, [0])
        self.assertListEqual(not_in_a, [2])
