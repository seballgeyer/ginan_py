"""
This module defines a `Measurements` class that represents a collection of measurement data associated with a
 satellite.

The class provides several methods for processing and visualizing the data, including subtraction of two
 `Measurements` objects, removal of the mean from each data series, plotting of the data, and computation
  of basic statistics for each data series.

Example usage:

    data_dict = {"_id": {"sat": "G01", "site": "ALIC    "}, "t": [1, 2, 3], "x": [4, 5, 6], "y": [7, 8, 9]}
    m1 = Measurements(data_dict)
    m1.demean()
    m1.plot()
    m2 = Measurements(data_dict)
    m3 = m1 - m2
    m3.stats()

Classes:
    Measurements: A class representing a collection of measurement data associated with a satellite.



Exceptions:
    ValueError: Raised when the input dictionary to the `Measurements` class constructor does not contain any data.

"""
import datetime
import logging

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Measurements:
    """
    A class to represent measurements taken from a satellite.

    This class stores measurement data as NumPy arrays, and provides methods for subtracting, demeaning, plotting,
    and computing statistics on the data.

    Attributes:
        sat (str): The name of the satellite that the measurements were taken from.
        id: An identifier for the measurements.
        epoch: A NumPy array of the times at which the measurements were taken.
        data (dict): A dictionary of NumPy arrays containing the measurement data.

    Methods:
        __init__(self, data_dict: dict): Initializes the Measurements object with data from a dictionary.
        __sub__(self, other): Computes the difference between two Measurements objects.
        demean(self): Removes the mean from the measurement data.
        plot(self, axis: plt.Axes): Plots the measurement data.
        stats(self): Computes and logs statistics on the measurement data.
    """

    def __init__(self, sat: str = "", identifier: dict = None, epoch: npt.ArrayLike = np.array([]), data: dict = None):
        """
        Initializes a Measurements object.

        :param sat: A string representing the ID of the satellite. Default is an empty string.
        :param identifier: A dictionary representing the ID of the measurements. The dictionary should contain a key "sat" with
                  the same value as the sat parameter, and may contain other ID fields. Default is an empty dictionary.
        :param epoch: A numpy array representing the time of the measurements in seconds since the Unix epoch. Default
                      is an empty numpy array.
        :param data: A dictionary representing the data fields of the measurements. The keys of the dictionary should be
                     strings representing the names of the data fields, and the values should be numpy arrays representing
                     the data for each field. Default is an empty dictionary.
        """
        self.sat = sat
        self.id = identifier if identifier is None else identifier
        self.epoch = epoch
        self.data = {} if data is None else data
        self.subset = slice(None, None, None)

    @classmethod
    def from_dictionary(cls, data_dict: dict) -> "Measurements":
        """
        Initializes a Measurements object.

        :param data_dict: A dictionary representing the data to be stored. The keys of the dictionary should be strings
                          representing the names of the data fields, and the values should be arrays representing the
                          data for each field. The first field in the dictionary should be "t", which represents the
                          epoch time. The remaining fields can be any other data fields to be stored.
        :raises ValueError: If the data_dict does not contain any data.
        :return the class
        """
        sat = data_dict["_id"]["sat"]
        identifier = data_dict["_id"]
        epoch = np.asarray(data_dict["t"])
        if max([len(value) for key, value in data_dict.items() if key not in ["t", "_id", "Epoch"]]) == 0:
            raise ValueError("No interesting data")
        data = {
            key: np.asarray(value) for key, value in data_dict.items() if key not in ["t", "_id"] and len(value) != 0
        }
        return cls(sat, identifier, epoch, data)  
    
    def __sub__(self, other):
        """
        Subtract another Measurements object from this one, element-wise.

        :param other: Another Measurements object to be subtracted from this one.
        :raises ValueError: If the Measurements objects have different satellite or site IDs.
        :raises ValueError: If there are no common keys between the data fields of the two Measurements objects.
        :returns: A new Measurements object representing the element-wise difference between this object and the other.
        """
        keys_to_compare = ["sat", "site"]
        if any(self.id[key] != other.id[key] for key in keys_to_compare):
            diffs = ", ".join(
                [
                    "%(key)s: %(self_id)s <> %(other_id)s"
                    % {"key": key, "self_id": self.id[key], "other_id": other.id[key]}
                    for key in keys_to_compare
                ]
            )
            raise ValueError(f"differencing Apples with oranges: {diffs}")

        self_keys = set(self.data.keys())
        other_keys = set(other.data.keys())
        common_keys = self_keys & other_keys
        missing_keys = (self_keys | other_keys) - common_keys

        if len(common_keys) == 0:
            raise ValueError("Warning: no common keys found between dictionaries")

        results = self
        _common, in_self, in_t = np.intersect1d(self.epoch, other.epoch, return_indices=True)
        in_self = np.where(in_self)[0].astype(int)
        in_t = np.where(in_t)[0].astype(int)
        results.epoch = self.epoch[in_self]

        results.data = {key: self.data[key][in_self] - other.data[key][in_t] for key in common_keys}

        if len(missing_keys) > 0:
            logger.warning("Warning: keys not present in both dictionaries:")
            logger.warning(f"Present in self.data only: {sorted(self_keys - other_keys)}")
            logger.warning(f"Present in other.data only: {sorted(other_keys - self_keys)}")

        return results

    def __lt__(self, other):
        order = ['series', 'sat', 'site', 'state', 'ax']  # Specify the order of fields for sorting
        for field in order:
            if field in self.id and field in other.id:
                if self.id[field] < other.id[field]:
                    return True
                elif self.id[field] > other.id[field]:
                    return False
            elif field in self.id:
                return False
            elif field in other.id:
                return True
        return False
    
    def demean(self):
        """
        Remove the mean value from each data field of this Measurements object.
        :return None.
        """
        for key in self.data:
            mean = self.data[key].mean(axis=0)
            logger.info(f"Removing mean of data {self.id}: {np.array2string(mean)}")
            self.data[key] -= mean

    def plot(self, axis: plt.Axes):
        """
        Plot the data stored in this Measurements object.

        :param axis: A Matplotlib Axes object to be used for the plot.
        """
        for key, value in self.data.items():
            if len(value.shape) > 1:
                for i, row in enumerate(value.T):
                    label = f"{key}[{i}]"
                    axis.plot(self.epoch, row, label=label)
            else:
                axis.plot(self.epoch, value, label=key)
        axis.legend()

      
    def get_stats(self):
        """
        Print statistics for the data stored in this Measurements object.
        """
        string = f"{self.id}"
        for key in self.data:
            rms = np.sqrt((self.data[key] ** 2).mean())
            string += f"\n\t{key} {self.data[key].mean(): .4e} sigma  {self.data[key].std(): .4e} RMS {rms:.4e}"
        logger.info(string)

    def select_range(self, tmin=None, tmax=None):
        if tmin is None:
            first_index = 0
        else:
            first_index = np.argmax(self.epoch >= tmin)
        if tmax is None:
            last_index = len(self.epoch)-1
        else:
            last_index = np.argmin(self.epoch <= tmax)-1
        self.subset = slice(first_index, last_index+1)



class MeasurementArray:
    def __init__(self) -> None:
        self.arr = []
        self.tmin = None
        self.tmax = None

    def __iter__(self):
        return iter(self.arr)
        
       
    @classmethod
    def from_mongolist(cls, data_lst: list) -> "MeasurementArray":
        object = cls()
        for data in data_lst:
            try:
                object.append(Measurements.from_dictionary(data))
            except:
                logger.debug("skyping this one")
        return object

    def find_minmax(self):
        try:
            self.tmin = min(obj.epoch[0] for obj in self.arr)
            self.tmax = max(obj.epoch[-1] for obj in self.arr)
        except:
            self.tmin = None
            self.tmax = None

    def sort(self):
        """
        sort the array by sat, site, series, state, ax
        """
        self.arr.sort()


    def adjust_slice(self, minutes_min=None, minutes_max=None) -> None:
        tmin = None
        tmax = None
        if minutes_min:
            tmin = self.tmin + datetime.timedelta(minutes=minutes_min)
        if minutes_max:
            tmax = self.tmax - datetime.timedelta(minutes=tmax)
        for data in self.arr:
            data.select_range(tmin=tmin, tmax=tmax)


    def append(self, foo_obj: Measurements) -> None:
        """
        Append a new time serie to the stack and update the minimum and maximum if required.
        """
        self.arr.append(foo_obj)

