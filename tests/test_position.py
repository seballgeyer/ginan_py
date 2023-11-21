#!/usr/bin/env python3
"""
TestPositions Tests for the Position class.
"""
import unittest
import datetime
import numpy as np
from sateda.data.position import Position
from sateda.data.measurements import MeasurementArray, Measurements


class TestPositions(unittest.TestCase):
    """
    TestPositions Tests for the Position class.
    """

    def test_diff(self):
        """
        test_rotate_enu Test the differencing function.
        For to positions, the difference should be the same as the difference.
        Extra complexity added in it as the 2 data does not have the same time stamps.
        """
        reference = MeasurementArray()
        data = MeasurementArray()
        time0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0 + datetime.timedelta(seconds=1), time0 + datetime.timedelta(seconds=2)],
            "x_0": [0, 0, 0],
            "x_1": [0, 0, 0],
            "x_2": [1, 0, -1],
        }
        reference.append(Measurements.from_dictionary(data_dict))
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0 - datetime.timedelta(seconds=1), time0, time0 + datetime.timedelta(seconds=1)],
            "x_0": [1, 1, 1],
            "x_1": [1, 1, 1],
            "x_2": [2, 3, 5],
        }
        data.append(Measurements.from_dictionary(data_dict))
        pos = Position(data=data, base=reference)
        self.assertEqual(len(pos.data.arr[0].data["x_2"]), 2)
        self.assertEqual(pos.data.arr[0].epoch[0], time0)
        self.assertEqual(pos.data.arr[0].epoch[1], time0 + datetime.timedelta(seconds=1))
        self.assertTrue(np.all(pos.data.arr[0].data["x_2"] == [2, 5]))

    def test_rotate_north(self):
        """
        test_rotate_enu Test the rotation function. For a point at the North Pole.
        The East and North are difficult to define, all the Z (x_2) is going in Up.
        """
        reference = MeasurementArray()
        data = MeasurementArray()
        time0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0 + datetime.timedelta(seconds=1)],
            "REC_POS_x_0": [0, 0],
            "REC_POS_x_1": [0, 0],
            "REC_POS_x_2": [1, 1],
        }
        reference.append(Measurements.from_dictionary(data_dict))
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0 + datetime.timedelta(seconds=1)],
            "REC_POS_x_0": [1, 1],
            "REC_POS_x_1": [1, 1],
            "REC_POS_x_2": [2, 3],
        }
        data.append(Measurements.from_dictionary(data_dict))
        pos = Position(data=data, base=reference)
        pos.rotate_enu()
        self.assertTrue(np.all(pos.data.arr[0].data["REC_POS_x_2"] == [1, 2]))

    def test_rotate_lat0lon0(self):
        """
        test_rotate_enu Test the rotation function for a point at lat=0 lon=0.
        x_1 (Y) is going in East, x_3 (Z) in North and x_0 (X) in Up.
        """
        reference = MeasurementArray()
        data = MeasurementArray()
        time0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {
            "_id": {"sat": "", "site": "Eq0"},
            "t": [time0, time0 + datetime.timedelta(seconds=1)],
            "REC_POS_x_0": [1, 1],
            "REC_POS_x_1": [0, 0],
            "REC_POS_x_2": [0, 0],
        }
        reference.append(Measurements.from_dictionary(data_dict))
        data_dict = {
            "_id": {"sat": "", "site": "Eq0"},
            "t": [time0, time0 + datetime.timedelta(seconds=1)],
            "REC_POS_x_0": [1.1, 1.1],
            "REC_POS_x_1": [0.2, 0.2],
            "REC_POS_x_2": [0.3, 0.3],
        }
        data.append(Measurements.from_dictionary(data_dict))
        pos = Position(data=data, base=reference)
        pos.rotate_enu()

        self.assertTrue(np.allclose(pos.data.arr[0].data["REC_POS_x_2"], [0.1, 0.1], atol=1e-15))  # U
        self.assertTrue(np.allclose(pos.data.arr[0].data["REC_POS_x_1"], [0.3, 0.3], atol=1e-15))  # N
        self.assertTrue(np.allclose(pos.data.arr[0].data["REC_POS_x_0"], [0.2, 0.2], atol=1e-15))  # E

    def test_rotate_lat0lon90(self):
        """
        test_rotate_enu Test the rotation function for a point at lat=0 lon=90.
        x_1 (Y) is going in Up, x_3 (Z) in North and x_0 (X) in -East.
        """
        reference = MeasurementArray()
        data = MeasurementArray()
        time0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {
            "_id": {"sat": "", "site": "Eq90"},
            "t": [time0, time0 + datetime.timedelta(seconds=1)],
            "REC_POS_x_0": [0, 0],
            "REC_POS_x_1": [1, 1],
            "REC_POS_x_2": [0, 0],
        }
        reference.append(Measurements.from_dictionary(data_dict))
        data_dict = {
            "_id": {"sat": "", "site": "Eq90"},
            "t": [time0, time0 + datetime.timedelta(seconds=1)],
            "REC_POS_x_0": [0.1, 0.1],
            "REC_POS_x_1": [1.2, 1.2],
            "REC_POS_x_2": [0.3, 0.3],
        }
        data.append(Measurements.from_dictionary(data_dict))
        pos = Position(data=data, base=reference)
        pos.rotate_enu()

        self.assertTrue(np.allclose(pos.data.arr[0].data["REC_POS_x_2"], [0.2, 0.2], atol=1e-15))  # U
        self.assertTrue(np.allclose(pos.data.arr[0].data["REC_POS_x_1"], [0.3, 0.3], atol=1e-15))  # N
        self.assertTrue(np.allclose(pos.data.arr[0].data["REC_POS_x_0"], [-0.1, -0.1], atol=1e-15))  # E
