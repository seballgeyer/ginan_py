"""
Testing set for measurements
"""
import datetime
import unittest

import numpy as np

from sateda.data.measurements import Measurements


class TestMeasurements(unittest.TestCase):
    """
    Unit test for the Measurements class
    """

    def setUp(self) -> None:
        self.meas = Measurements()
        time_init = datetime.datetime(2023, 1, 1, 0, 0, 0)
        self.meas.epoch = np.array([time_init + datetime.timedelta(minutes=i) for i in range(60)])
        print(len(self.meas.epoch))

    def test_select_range_tmin(self):
        """
        test the select_range function.
        For a defined tmin , the subset should be equal to the slice of the epoch array
        """
        tmin = datetime.datetime(2023, 1, 1, 0, 5, 0)
        self.meas.select_range(tmin=tmin, tmax=None)
        results = slice(5, len(self.meas.epoch))
        self.assertEqual(self.meas.subset, results)

    def test_select_range_tmax(self):
        """
        test the select_range function.
        For a defined tmax, the subset should be equal to the slice of the epoch array
        """
        tmax = datetime.datetime(2023, 1, 1, 0, 55, 0)
        self.meas.select_range(tmin=None, tmax=tmax)
        results = slice(0, 56)
        self.assertEqual(self.meas.subset, results)

    def test_polyfit(self):
        """
        test the polyfit function, fiting a polynomial and returnin the coeffiction.
        """
        time_init = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {
            "_id": {"sat": "G01", "site": "ALIC    "},
            "t": [
                time_init + datetime.timedelta(seconds=1),
                time_init + datetime.timedelta(seconds=2),
                time_init + datetime.timedelta(seconds=3),
            ],
            "x": [4.0, 5.0, 6.0],
            "y": [7.0, 8.0, 9.0],
        }
        meas = Measurements.from_dictionary(data_dict)
        meas.polyfit()
        fit = meas.info["Fit"]
        self.assertAlmostEqual(fit["x"][0], 1)
        self.assertAlmostEqual(fit["y"][0], 1)
        self.assertAlmostEqual(fit["x"][1], 4)
        self.assertAlmostEqual(fit["y"][1], 7)

    def test_detrend(self):
        """
        Test the detrend function. Detrend the polynomial fit of the data.
        """
        time_init = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {
            "_id": {"sat": "G01", "site": "ALIC    "},
            "t": [
                time_init + datetime.timedelta(seconds=1),
                time_init + datetime.timedelta(seconds=2),
                time_init + datetime.timedelta(seconds=3),
            ],
            "x": [4.0, 5.0, 6.0],
            "y": [7.0, 8.0, 9.0],
        }
        meas = Measurements.from_dictionary(data_dict)
        meas.detrend(degree=0)
        self.assertAlmostEqual(meas.data["x"][0], -1)
        self.assertAlmostEqual(meas.data["y"][0], -1)
        self.assertAlmostEqual(meas.data["x"][1], 0)
        self.assertAlmostEqual(meas.data["y"][1], 0)
        self.assertAlmostEqual(meas.data["x"][2], 1)
        self.assertAlmostEqual(meas.data["y"][2], 1)

    def test_find_gaps(self):
        """
        Test the find_gaps function.
        if the time between 2 points is more than delta defined in find_gaps function, insert a NaN
        """
        time_init = datetime.datetime(2021, 1, 1, 0, 0, 0)
        deltatt = np.array([i for i in range(12)])
        deltatt[3:] = deltatt[3:] + 60
        deltatt[6:] = deltatt[6:] + 60
        deltatt[7:] = deltatt[7:] + 400
        deltatt[9:] = deltatt[9:] + 400
        deltatt[10:] += 60
        data_dict = {
            "_id": {"sat": "G01", "site": "ALIC    "},
            "t": [time_init + datetime.timedelta(seconds=int(t)) for t in deltatt],
            "x": [1.0] * len(deltatt),
        }
        meas = Measurements.from_dictionary(data_dict)
        meas.find_gaps(delta=1)
        for i in [3, 8, 11]:
            self.assertTrue(np.isnan(meas.data["x"][i]))
