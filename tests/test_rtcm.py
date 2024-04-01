import unittest

from sateda.io.rtcm.rtcm1006 import Rtcm1006
from sateda.io.rtcm.rtcm1019 import Rtcm1019
from sateda.io.rtcm.rtcm1077 import Rtcm1077

class TestRtcm1006(unittest.TestCase):
    def test_encode(self):
        with open("data/msg1006_3.rtcm", "rb") as f:
            data = f.read()
        decoded = Rtcm1006.decode(data)
        print(decoded)
        self.assertTrue(False)
   # assert

class TestRtcm1019(unittest.TestCase):
    def test_encode(self):
        with open("data/msg1019_2.rtcm", "rb") as f:
            data = f.read()
        decoded = Rtcm1019.decode(data)
        print(decoded)
        self.assertTrue(False)
   # assert


class TestRtcm1077(unittest.TestCase):
    def test_encode(self):
        with open("data/msg1077_1.rtcm", "rb") as f:
            data = f.read()
        decoded = Rtcm1077.decode(data)
        print(decoded)
        import json
        pretty_json = json.dumps(decoded.asdict(), indent=4)
        print(pretty_json)
        self.assertTrue(False)
   # assert