"""
Testing set for Helmert transform 
"""
import unittest

import numpy as np

from sateda.core.transform.helmert import HelmertTransform


class TestHelmert(unittest.TestCase):
    def setUp(self) -> None:
        np.random.seed(0)
        return super().setUp()

    def test_helmert_translation(self):
        helmert = HelmertTransform(translation=[1, 2, 3])
        vector = np.array([1, 2, 3])
        expected = np.array([2, 4, 6])
        self.assertTrue(np.allclose(helmert.apply(vector), expected))

    def test_helmert_translation_multiarray(self):
        helmert = HelmertTransform(translation=[1, 2, 3])
        vector = np.array([[1, 2, 3], [6, 8, 10]])
        expected = np.array([[2, 4, 6], [7, 10, 13]])
        self.assertTrue(np.allclose(helmert.apply(vector), expected))

    def test_helmert_rotation_z(self):
        helmert = HelmertTransform(rotation=[0, 0, 90])
        vector = np.array([1, 0, 0])
        expected = np.array([0, 1, 0])
        self.assertTrue(np.allclose(helmert.apply(vector), expected))

    def test_helmert_rotation_x(self):
        helmert = HelmertTransform(rotation=[90, 0, 0])
        vector = np.array([0, 0, 1])
        expected = np.array([0, -1, 0])
        self.assertTrue(np.allclose(helmert.apply(vector), expected))

    def test_helmert_rotation_x_multiple(self):
        helmert = HelmertTransform(rotation=[90, 0, 0])
        vector = np.array([[0, 0, 1], [0, 1, 0]])
        expected = np.array([[0, -1, 0], [0, 0, 1]])
        self.assertTrue(np.allclose(helmert.apply(vector), expected))

    def test_fit_translation(self):
        helmert = HelmertTransform(translation=[1e-6, 2e-6, 3e-6], rotation=[0, 0, 0], config={"degrees": True})
        vector = np.random.rand(100, 3)
        target = helmert.apply(vector)
        helmert2 = HelmertTransform()
        for _i in range(10):
            helmert2.fit(vector, target, params={"translation": True, "rotation": False, "scale": False})
        self.assertTrue(np.all(helmert.get_params() - helmert2.get_params() < 1e-16))

    def test_fit_scale(self):
        helmert = HelmertTransform(translation=[0, 0, 0], rotation=[0, 0, 0], scale=5.2e-5, config={"degrees": True})
        vector = np.random.rand(100, 3)
        target = helmert.apply(vector)
        helmert2 = HelmertTransform()
        for _i in range(10):
            helmert2.fit(vector, target, params={"translation": False, "rotation": False, "scale": True})
        self.assertTrue(np.all(helmert.get_params() - helmert2.get_params() < 1e-16))

    def test_fit_rot(self):
        helmert = HelmertTransform(
            translation=[0, 0, 0], rotation=[1 / 3600.0, 2 / 3600.0, 0], scale=0, config={"degrees": True}
        )

        vector = np.random.rand(100, 3)
        target = helmert.apply(vector)
        helmert2 = HelmertTransform()
        for _i in range(10):
            helmert2.fit(vector, target, params={"translation": False, "rotation": True, "scale": False})
        self.assertTrue(np.all(helmert.get_params() - helmert2.get_params() < 1e-16))

    def test_fit_combined(self):
        helmert = HelmertTransform(
            translation=[1e-3, 1e-4, 2e-3],
            rotation=[1 / 3600.0, 2 / 3600.0, 4 / 3600.0],
            scale=1e-6,
            config={"degrees": True},
        )
        vector = np.random.rand(100, 3)
        target = helmert.apply(vector)
        helmert2 = HelmertTransform()
        for _i in range(10):
            helmert2.fit(vector, target)
        print(helmert.get_params() - helmert2.get_params())
        self.assertTrue(np.all(helmert.get_params() - helmert2.get_params() < 1e-15))
