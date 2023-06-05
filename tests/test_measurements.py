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
        
    def test_polyfit(self):
        t0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {"_id": {"sat": "G01", "site": "ALIC    "}, 
                    "t": [t0 + datetime.timedelta(seconds=1), t0 + datetime.timedelta(seconds=2), t0 + datetime.timedelta(seconds=3)],
                    "x": [4.0, 5.0, 6.0], 
                    "y": [7.0, 8.0, 9.0]}
        m1 = Measurements.from_dictionary(data_dict)
        print(m1.data)
        print(m1)
        fit = m1.polyfit()
        print(fit)
        print(fit['x'][0])
        self.assertAlmostEqual( fit['x'][0] , 1)
        self.assertAlmostEqual( fit['y'][0] , 1)
        self.assertAlmostEqual( fit['x'][1] , 4)
        self.assertAlmostEqual( fit['y'][1] , 7)
        
    def test_detrend(self):
        """
        Test the detrend function
        """
        t0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {"_id": {"sat": "G01", "site": "ALIC    "}, 
                    "t": [t0 + datetime.timedelta(seconds=1), t0 + datetime.timedelta(seconds=2), t0 + datetime.timedelta(seconds=3)],
                    "x": [4.0, 5.0, 6.0], 
                    "y": [7.0, 8.0, 9.0]}
        m1 = Measurements.from_dictionary(data_dict)
        print(m1.epoch)
        m1.detrend(degree=0)
        self.assertAlmostEqual( m1.data['x'][0], -1)
        self.assertAlmostEqual( m1.data['y'][0], -1)
        self.assertAlmostEqual( m1.data['x'][1], 0)
        self.assertAlmostEqual( m1.data['y'][1], 0)
        self.assertAlmostEqual( m1.data['x'][2], 1)
        self.assertAlmostEqual( m1.data['y'][2], 1)
        
    #unit test to test a function "find_gaps" in measurements.py which would numpy array of epochs, and insert a nan when the data are more than 15 minutes apart. However if there is only one point in the segment, link it to the closest in time
    def test_find_gaps(self):
        t0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        #generate an array deltat of 12 elements being 5 second apart, with a gap of 60 seconds between the 3rd and 4th element, 60 seconds between the 6th and 7th element, 400 seconds between the 9th and 10th element
        deltatt = np.array([i for i in range(12)])
        deltatt[3:] = deltatt[3:] + 60
        deltatt[6:] = deltatt[6:] + 60
        deltatt[7:] = deltatt[7:] + 400
        deltatt[9:] = deltatt[9:] + 400
        deltatt[10:] += 60
        data_dict = {"_id": {"sat": "G01", "site": "ALIC    "}, 
                    "t": [t0 + datetime.timedelta(seconds=int(t)) for t in deltatt],
                    "x": [1.0] * len(deltatt),}
        m1 = Measurements.from_dictionary(data_dict)
        m1.find_gaps()
        for i in [3,8,11]:
            self.assertTrue(np.isnan(m1.data['x'][i] ))
