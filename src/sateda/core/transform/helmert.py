"""
This module contains classes for performing Helmert transformations on sets of coordinates.
"""

from typing import List
import logging
import warnings

import numpy as np
from sklearn.model_selection import train_test_split
import sys 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


class ResidualCheck:
    """
    Class for checking residuals during Helmert transformation iterations.

    Args:
        previous (float): The previous residual value.
        new (float): The new residual value.
        iteration_params (dict): A dictionary containing the iteration parameters.

    Attributes:
        previous (float): The previous residual value.
        new (float): The new residual value.
        iteration_params (dict): A dictionary containing the iteration parameters.
        what (str): A string describing what was checked during the residual check.

    Returns:
        bool: True if any of the residual checks pass, False otherwise.
    """

    def __init__(self, previous: float, new: float, iteration_params: dict) -> None:
        """
        Initializes a ResidualCheck object.

        Args:
            previous (float): The previous residual value.
            new (float): The new residual value.
            iteration_params (dict): A dictionary containing the iteration parameters.
        """
        self.previous = previous
        self.new = new
        self.iteration_params = iteration_params
        self.what = "nothing checked"

    def __call__(self) -> bool:
        """
        Checks the residuals and returns True if any of the checks pass, False otherwise.

        Returns:
            bool: True if any of the residual checks pass, False otherwise.
        """
        # Minimum residuals norm
        if self._check_min_residuals_norm():
            return True
        # Absolute difference in residuals
        if self._check_min_delta_residuals():
            return True
        # Relative difference in residuals
        if self._check_min_relative_residuals():
            return True
        return False

    def _check_min_residuals_norm(self) -> bool:
        """
        Checks if the new residual value is less than the minimum residuals norm.

        Returns:
            bool: True if condition is meet, False otherwise.
        """
        if self.new < self.iteration_params["min_residuals_norm"]:
            self.what = (
                f"Minimum residuals norm ({self.iteration_params['min_residuals_norm']}) reached. (val. {self.new})"
            )
            return True
        return False

    def _check_min_delta_residuals(self) -> bool:
        """
        Checks if the absolute difference between residual values is less than the minimum delta residuals.

        Returns:
            bool: True if condition is meet, False otherwise.
        """
        if abs(self.new - self.previous) < self.iteration_params["min_delta_residuals"]:
            self.what = (
                f"Minimum delta residuals ({self.iteration_params['min_delta_residuals']}) "
                f"reached. (val. {abs(self.new - self.previous)})"
            )
            return True
        return False

    def _check_min_relative_residuals(self) -> bool:
        """
        Checks if the relative difference between residual values is less than the minimum relative residuals.

        Returns:
            bool: True if condition is meet, False otherwise.
        """
        try:
            if abs((self.previous - self.new) / self.previous) < self.iteration_params["min_relative_residuals"]:
                self.what = (
                    f"Minimum relative residuals norm ({self.iteration_params['min_relative_residuals']}) reached."
                )
                return True
        except ZeroDivisionError:
            pass
        return False

    def get_previous_residual(self) -> float:
        """
        Returns the previous residual value.

        Returns:
            float: The previous residual value.
        """
        return self.previous

    def get_new_residual(self) -> float:
        """
        Returns the new residual value.

        Returns:
            float: The new residual value.
        """
        return self.new

    def get_iteration_params(self) -> dict:
        """
        Returns the iteration parameters.

        Returns:
            dict: A dictionary containing the iteration parameters.
        """
        return self.iteration_params


class HelmertTransform:
    """
    A class representing a Helmert transformation, which consists of a scaling factor, a rotation vector, and a
    translation vector. The transformation can be applied to a set of coordinates using the `apply` method.

    :param scale: The scaling factor. Default is 1.0.
    :type scale: float
    :param rotation: The rotation vector, as a list of three angles in degrees. Default is [0, 0, 0].

    """

    def __init__(
        self, scale: float = 0.0, rotation: List[float] = None, translation: List[float] = None, config: dict = None
    ):
        self.scale = scale
        self.rotation = np.array(rotation or [0, 0, 0], dtype=np.float64)
        self.translation = np.array(translation or [0, 0, 0], dtype=np.float64)
        if config is None:
            config = {}
        degrees = config.get("degrees", True)
        self.scaling_factor = config.get("scaling_factor", 1.0)
        self.scale *= self.scaling_factor
        if degrees:
            self.rotation = np.deg2rad(self.rotation)

    def __str__(self) -> str:
        np.set_printoptions(precision=4, suppress=True, formatter={"float": "{:0.4e}".format})
        return (
            f"HelmertTransform(scale={self.scale/self.scaling_factor:.4e}, "
            f"rotation={np.rad2deg(self.rotation)}, translation={self.translation})"
        )

    def get_params(self) -> np.array:
        """
        Return the transformation parameters as a numpy array of shape (7,).

        :return: The transformation parameters.
        :rtype: numpy.array
        """
        return np.concatenate((self.translation, [self.scale], self.rotation))

    def as_rotation_matrix(self) -> np.array:
        """
        Return the rotation matrix corresponding to the rotation vector.

        :return: The rotation matrix, as a numpy array of shape (3, 3).
        :rtype: numpy.array
        """
        cos_angle = np.cos(self.rotation)
        sin_angle = np.sin(self.rotation)
        # fmt: off
        rot_x = np.array([[1, 0, 0],
                          [0, cos_angle[0], -sin_angle[0]],
                          [0, sin_angle[0], cos_angle[0]]])
        rot_y = np.array([[cos_angle[1], 0, sin_angle[1]],
                          [0, 1, 0],
                          [-sin_angle[1], 0, cos_angle[1]]])
        rot_z = np.array([[cos_angle[2], -sin_angle[2], 0],
                          [sin_angle[2], cos_angle[2], 0],
                          [0, 0, 1]])
        # fmt: on
        return rot_z @ rot_y @ rot_x

    def jac_rotation(self) -> (np.array, np.array, np.array):
        """
        jac_rotation the jacobian of the rotation matrix corresponding to the rotation vector.
        """
        cos_angle = np.cos(self.rotation)
        sin_angle = np.sin(self.rotation)
        # fmt: off
        rot_x = np.array([[1, 0, 0],
                          [0, cos_angle[0], sin_angle[0]],
                          [0, -sin_angle[0], cos_angle[0]]])
        rot_y = np.array([[cos_angle[1], 0, -sin_angle[1]],
                          [0, 1, 0],
                          [sin_angle[1], 0, cos_angle[1]]])
        rot_z = np.array([[cos_angle[2], sin_angle[2], 0],
                          [-sin_angle[2], cos_angle[2], 0],
                          [0, 0, 1]])
        rot_x_jac = np.array([[0, 0, 0],
                              [0, -sin_angle[0], cos_angle[0]],
                              [0, -cos_angle[0], -sin_angle[0]]])
        rot_y_jac = np.array([[-sin_angle[1], 0, -cos_angle[1]],
                              [0, 0, 0],
                              [cos_angle[1], 0, sin_angle[1]]])
        rot_z_jac = np.array([[-sin_angle[2], cos_angle[2], 0],
                              [-cos_angle[2], -sin_angle[2], 0],
                              [0, 0, 0]])
        # fmt: on
        return rot_z @ rot_y @ rot_x_jac, rot_z @ rot_y_jac @ rot_x, rot_z_jac @ rot_y @ rot_x

    def apply(self, data: np.array) -> np.array:
        """
        Apply the Helmert transformation to a set of coordinates.

        :param data: The coordinates to transform, as a numpy array of shape (n, 3).
        :type data: numpy.array
        :return: The transformed coordinates, as a numpy array of shape (n, 3).
        :rtype: numpy.array
        """
        data = np.array(data, dtype=np.float64)
        return (1 + self.scale) * (data @ self.as_rotation_matrix().T) + self.translation

    def jacobian(self, data: np.array, params=None) -> np.array:
        """
        Return the Jacobian matrix of the Helmert transformation.

        :param data: The coordinates to transform, as a numpy array of shape (n, 3).
        :type data: numpy.array
        :return: The Jacobian matrix, as a numpy array of shape (7, n, 3).
        :rtype: numpy.array
        """
        if params is None:
            params = {"translation": True, "rotation": True, "scale": True}
        data = np.array(data, dtype=np.float64)
        rot_jac = self.jac_rotation()
        rot = self.as_rotation_matrix()
        translation_jac = np.eye(3)
        n_param = 0
        if params["translation"]:
            n_param += 3
        if params["rotation"]:
            n_param += 3
        if params["scale"]:
            n_param += 1
        jacobian = np.zeros((data.shape[0], 3, n_param))
        idx = 0
        if params["translation"]:
            jacobian[:, :, :3] = np.tile(translation_jac, (data.shape[0], 1, 1))
            idx += 3
        if params["scale"]:
            jacobian[:, :, idx] = data @ rot
            idx += 1
        if params["rotation"]:
            jacobian[:, :, idx] = data @ rot_jac[0] * (1 + self.scale)
            jacobian[:, :, idx + 1] = data @ rot_jac[1] * (1 + self.scale)
            jacobian[:, :, idx + 2] = data @ rot_jac[2] * (1 + self.scale)
        return jacobian

    def fit_single_step(self, data: np.array, target: np.array, params: dict = None) -> None:
        """
        Fit the Helmert transformation to a set of coordinates.

        :param data: The coordinates to transform, as a numpy array of shape (n, 3).
        :type data: numpy.array
        :param target: The target coordinates, as a numpy array of shape (n, 3).
        :type target: numpy.array
        :param params: A dictionary containing the parameters to fit.
                        Default is {'translation': True, 'rotation': True, 'scale': True}.
        :type params: dict
        :return: The fitted transformation parameters, as a numpy array of shape (7,).
        :rtype: numpy.array
        """
        if params is None:
            params = {"translation": True, "rotation": True, "scale": True}
        residuals = self.apply(data) - target
        design = self.jacobian(data, params)
        residuals = residuals.reshape(-1)
        design = design.reshape((design.shape[0] * design.shape[1], -1))
        delta = np.linalg.inv(design.transpose() @ design) @ design.transpose() @ residuals
        idx = 0
        if params["translation"]:
            self.translation -= delta[:3]
            idx += 3
        if params["scale"]:
            self.scale -= delta[idx]
            idx += 1
        if params["rotation"]:
            self.rotation -= delta[idx:]

    def fit(self, data: np.array, target: np.array, params: dict = None, iteration_params: dict = None) -> None:
        """
        Fit the Helmert transformation to a set of coordinates using a non-linear least squares approach.

        :param data: The coordinates to transform, as a numpy array of shape (n, 3).
        :type data: numpy.array
        :param target: The target coordinates, as a numpy array of shape (n, 3).
        :type target: numpy.array
        :param params: A dictionary containing the parameters to fit.
            Default is {'translation': True, 'rotation': True, 'scale': True}.
        :type params: dict
        :param iteration_params: A dictionary containing the iteration parameters.
            Default is {'max_iter': 100,
                        'min_residuals_norm': 1e-6,
                        'min_delta_residuals': 1e-9,
                        'min_relative_residuals': 1e-9}.
        :type iteration_params: dict
        :return: None
        """
        if params is None:
            params = {"translation": True, "rotation": True, "scale": True}
        if iteration_params is None:
            iteration_params = {
                "max_iter": 100,
                "min_residuals_norm": 1e-16,
                "min_delta_residuals": 1e-16,
                "min_relative_residuals": 1e-16,
                "test_size": 0.2,
                "batch_size": 256,
            }
        data_train, data_test, target_train, target_test = train_test_split(
            data, target, test_size=iteration_params["test_size"], random_state=42
        )
        residuals_norm = np.inf
        previous_residuals_norm = np.inf
        iteration = 0
        while iteration < iteration_params["max_iter"]:
            for batch_start in range(0, data_train.shape[0], iteration_params["batch_size"]):
                batch_end = min(batch_start + iteration_params["batch_size"], data.shape[0])
                self.fit_single_step(data_train[batch_start:batch_end], target_train[batch_start:batch_end], params)
            residuals_norm = np.linalg.norm(self.apply(data_test) - target_test)
            residual_check = ResidualCheck(residuals_norm, previous_residuals_norm, iteration_params)
            if residual_check():
                logger.info(residual_check.what)
                break
            previous_residuals_norm = residuals_norm
            iteration += 1
        else:
            warnings.warn(f"Maximum number of iterations ({iteration_params['max_iter']}) reached.")
            return
        logger.info(f"converged after {iteration} iterations")