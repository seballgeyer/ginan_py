import unittest

import numpy as np
from sateda.core.time import Time, TimeSystem
from sateda.core.coordinates import Eop


class SofaCoobook(unittest.TestCase):
    def setUp(self) -> None:
        self.time = Time.from_components(2007, 4, 5, 12, 0, 0, 0, timesystem=TimeSystem.UTC)
        self.eop = Eop(self.time)
        self.eop.xp = 0.0349282 / 3600 * np.pi / 180
        self.eop.yp = 0.4833163 / 3600 * np.pi / 180
        self.eop.ut1_utc = -0.072073685

    def test_checktime(self) -> None:
        d1, d2 = self.time.to_tt().to_jd()
        self.assertAlmostEqual(self.time.to_tt().to_mjd()[1], 0.500754444444444, 10)
        self.assertAlmostEqual(self.time.to_utc().to_mjd()[1] + self.eop.ut1_utc / 86400, 0.499999165813831, 10)

    def test_iau2000(self):
        self.eop.iau2000()
        self.assertAlmostEqual(self.eop.X, 0.000712264729708, 15)
        self.assertAlmostEqual(self.eop.Y, 0.000044385250265, 15)
        self.assertAlmostEqual(self.eop.s * 3600 * 180 / np.pi, -0.002200496, 9)
        self.assertAlmostEqual(self.eop.era, 13.318492966097 * np.pi / 180.0, 13)
        expected_rot = np.array(
            [
                [0.973104317697512, 0.230363826239227, -0.000703163482268],
                [-0.230363800456136, 0.973104570632777, 0.000118545366806],
                [0.000711560162777, 0.000046626403835, 0.999999745754024],
            ]
        )
        print(self.eop.rot - expected_rot)
        self.assertTrue(np.allclose(self.eop.rot, expected_rot, rtol=0.0, atol=1e-14))

    def test_iau2006(self):
        self.eop.iau2006()
        print(self.eop.X, self.eop.Y, self.eop.s)
        self.assertAlmostEqual(self.eop.X, 0.000712264729525, 15)
        self.assertAlmostEqual(self.eop.Y, 0.000044385248875, 15)
        self.assertAlmostEqual(self.eop.s * 3600 * 180 / np.pi, -0.002200475, 9)
        self.assertAlmostEqual(self.eop.era, 13.318492966097 * np.pi / 180.0, 13)
        expected_rot = np.array(
            [
                [0.973104317697536, 0.230363826239128, -0.000703163481769],
                [-0.230363800456036, 0.973104570632801, 0.000118545368117],
                [0.000711560162594, 0.000046626402444, 0.999999745754024],
            ]
        )
        self.assertTrue(np.allclose(self.eop.rot, expected_rot, rtol=0.0, atol=1e-14))


if __name__ == "__main__":
    unittest.main()
