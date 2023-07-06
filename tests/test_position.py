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
        test_rotate_enu Test the rotation function. 
        """
        reference = MeasurementArray()
        data  = MeasurementArray()
        time0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0+datetime.timedelta(seconds=1)],
            "x_0": [0, 0],
            "x_1": [0, 0],
            "x_2": [1, 1],
        }
        reference.append(Measurements.from_dictionary(data_dict))
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0+datetime.timedelta(seconds=1)],
            "x_0": [1,1],
            "x_1": [1, 1],
            "x_2": [2, 3],
        }
        data.append(Measurements.from_dictionary(data_dict))
        pos = Position(data=data, base=reference)
        self.assertTrue(np.alltrue(pos.data.arr[0].data["x_2"] == [1,2]))


    def test_rotate_north(self):
        """
        test_rotate_enu Test the rotation function. 
        """
        reference = MeasurementArray()
        data  = MeasurementArray()
        time0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0+datetime.timedelta(seconds=1)],
            "x_0": [0, 0],
            "x_1": [0, 0],
            "x_2": [1, 1],
        }
        reference.append(Measurements.from_dictionary(data_dict))
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0+datetime.timedelta(seconds=1)],
            "x_0": [1,1],
            "x_1": [1, 1],
            "x_2": [2, 3],
        }
        data.append(Measurements.from_dictionary(data_dict))
        pos = Position(data=data, base=reference)
        pos.rotate_enu()
        self.assertTrue(np.alltrue(pos.data.arr[0].data["x_2"] == [1,2]))


    def test_rotate_lat0lon0(self):
        """
        test_rotate_enu Test the rotation function. 
        """
        reference = MeasurementArray()
        data  = MeasurementArray()
        time0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0+datetime.timedelta(seconds=1)],
            "x_0": [1,1],
            "x_1": [0, 0],
            "x_2": [0, 0],
        }
        reference.append(Measurements.from_dictionary(data_dict))
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0+datetime.timedelta(seconds=1)],
            "x_0": [1.1,1.1],
            "x_1": [0.2, 0.2],
            "x_2": [0.3, 0.3],
            
        }
        data.append(Measurements.from_dictionary(data_dict))
        pos = Position(data=data, base=reference)
        pos.rotate_enu()
        
        self.assertTrue(np.allclose(pos.data.arr[0].data["x_2"] , [0.1,0.1], atol=1e-15))
        self.assertTrue(np.allclose(pos.data.arr[0].data["x_1"] , [0.3,0.3], atol=1e-15))
        self.assertTrue(np.allclose(pos.data.arr[0].data["x_0"] , [0.2,0.2], atol=1e-15))
        
        
    def test_rotate_lat0lon90(self):
        """
        test_rotate_enu Test the rotation function. 
        """
        reference = MeasurementArray()
        data  = MeasurementArray()
        time0 = datetime.datetime(2021, 1, 1, 0, 0, 0)
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0+datetime.timedelta(seconds=1)],
            "x_0": [0, 0],
            "x_1": [1,1],
            "x_2": [0, 0],
        }
        reference.append(Measurements.from_dictionary(data_dict))
        data_dict = {
            "_id": {"sat": "", "site": "North"},
            "t": [time0, time0+datetime.timedelta(seconds=1)],
            "x_0": [0.1, 0.1],
            "x_1": [1.2, 1.2],
            "x_2": [0.3, 0.3],
        }
        data.append(Measurements.from_dictionary(data_dict))
        pos = Position(data=data, base=reference)
        pos.rotate_enu()
        
        self.assertTrue(np.allclose(pos.data.arr[0].data["x_2"] , [0.2,0.2], atol=1e-15))
        self.assertTrue(np.allclose(pos.data.arr[0].data["x_1"] , [0.3,0.3], atol=1e-15))
        self.assertTrue(np.allclose(pos.data.arr[0].data["x_0"] , [-0.1,-0.1], atol=1e-15))