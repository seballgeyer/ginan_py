"""
Testing set for measurements
"""
import unittest

import numpy as np
import datetime

from sateda.data.measurements import Measurements

class TestMeasurements(unittest.TestCase):
    def setUp(self) -> None:
        self.M = Measurements()
        d = datetime.datetime(2023, 1, 1, 0 , 0, 0)
        self.M.epoch = np.array([ d + datetime.timedelta(minutes=i) for i in range(60)])
        print(len(self.M.epoch))
    
    def test_select_range_tmin(self):
        tmin = datetime.datetime(2023,1,1,0,5,0)
        self.M.select_range(tmin=tmin, tmax=None)
        results = slice( 5,len(self.M.epoch))
        self.assertEqual(self.M.subset,results)

    def test_select_range_tmax(self):
        tmax = datetime.datetime(2023,1,1,0,55,0)
        self.M.select_range(tmin=None, tmax=tmax)
        results = slice( 0,56)
        self.assertEqual(self.M.subset,results)