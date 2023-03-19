import unittest

from sateda.utils.common import find_common


class MyClass:
    def __init__(self, id_, other_attribute):
        self.id = id_
        self.other_attribute = other_attribute

    def __str__(self):
        return f"{self.id}"


class Testcommon(unittest.TestCase):
    """
    Class testing pattern
    """

    def test_common(self) -> None:
        # Sample data
        dataset1 = [
            MyClass({"id1": "value1"}, "attribute1"),
            MyClass({"id2": "value2"}, "attribute2"),
            MyClass({"id3": "value3"}, "attribute3"),
        ]

        dataset2 = [
            MyClass({"id2": "value2"}, "attribute4"),
            MyClass({"id3": "value3"}, "attribute5"),
            MyClass({"id4": "value4"}, "attribute6"),
        ]

        common, not_in_dataset2, not_in_dataset1 = find_common(dataset1, dataset2)
        self.assertEqual(len(common), 2)  # add assertion here
        self.assertEqual(len(not_in_dataset2), 1)  # add assertion here
        self.assertEqual(len(not_in_dataset1), 1)  # add assertion here
        self.assertListEqual(common, [(1, 0), (2, 1)])
        self.assertListEqual(not_in_dataset2, [0])
        self.assertListEqual(not_in_dataset1, [2])
