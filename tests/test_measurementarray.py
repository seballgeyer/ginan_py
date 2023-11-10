"""
Testing set for measurements
"""
import datetime
import unittest

import numpy as np

from sateda.data.measurements import MeasurementArray, Measurements


class TestsMeasurementArray(unittest.TestCase):
    """
    TestsMeasurementArray _summary_

    :param _type_ unittest: _description_
    """

    def test_substract(self):
        """
        test_substract Testing the substraction between 2 dataset.
        The substraction should be donne on common epochs and identical sat / site combination
        """
        reference = MeasurementArray()
        data = MeasurementArray()
        t0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        # generate an array deltat of 12 elements being 5 second apart, with a gap of 60 seconds between the 3rd and 4th element, 60 seconds between the 6th and 7th element, 400 seconds between the 9th and 10th element
        deltatt = np.array([i for i in range(12)])
        deltatt[3:] = deltatt[3:] + 60
        deltatt[6:] = deltatt[6:] + 60
        deltatt[7:] = deltatt[7:] + 400
        deltatt[9:] = deltatt[9:] + 400
        deltatt[10:] += 60
        data_dict = {
            "_id": {"sat": "G01", "site": "ALIC"},
            "t": [t0 + datetime.timedelta(seconds=int(t)) for t in deltatt],
            "x": [1.0] * len(deltatt),
        }
        reference.append(Measurements.from_dictionary(data_dict))
        data_dict = {
            "_id": {"sat": "G01", "site": "TONG"},
            "t": [t0 + datetime.timedelta(seconds=int(t)) for t in deltatt],
            "x": [3.0] * len(deltatt),
        }
        reference.append(Measurements.from_dictionary(data_dict))
        data_dict = {
            "_id": {"sat": "G01", "site": "TONG"},
            "t": [t0 + datetime.timedelta(seconds=int(t)) for t in deltatt],
            "x": [1.0] * len(deltatt),
        }
        data.append(Measurements.from_dictionary(data_dict))
        res = reference - data
        self.assertEqual(len(res.arr), 1)


if __name__ == "__main__":
    unittest.main()
