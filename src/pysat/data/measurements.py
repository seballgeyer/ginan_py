import logging

import numpy.typing as npt
import numpy as np

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Measurements:
    def __init__(self, d: dict):
        self.sat: str = d["_id"]["sat"]
        self.id = d["_id"]
        self.t: npt.ArrayLike = np.asarray(d["t"])
        self.data: dict = {}
        for key in d:
            if key not in ["t", "_id"]:
                if len(d[key]) != 0:
                    self.data[key] = np.asarray(d[key])
        if len(self.data) == 0:
            raise ValueError("no data")

    def __sub__(self, other):
        if self.id["sat"] != other.id["sat"] or self.id["site"] != other.id["site"]:
            raise Exception(
                f"differencing Apples with oranges:"
                f" sat: {self.id['sat']} <> {other.id['sat']}"
                f" site: {self.id['site']} <> {other.id['site']}"
            )
        results = self
        common, in_self, in_t = np.intersect1d(self.t, other.t, return_indices=True)
        in_self = np.where(in_self)[0].astype(int)
        in_t = np.where(in_t)[0].astype(int)
        results.t = self.t[in_self]
        results.data = {key: self.data[key][in_self] - other.data[key][in_t] for key in self.data}
        return results

    def demean(self):
        for key in self.data:
            mean = self.data[key].mean(axis=0)
            logger.info(f"Removing mean of data {self.id}: {np.array2string(mean)}")
            self.data[key] -= mean

    def plot(self, ax: plt.Axes):
        for key in self.data:
            ax.plot(self.t, self.data[key])

    def stats(self):
        for key in self.data:
            rms = np.sqrt((self.data[key] ** 2).mean())
            logger.info(
                f"{self.id}, {key} {self.data[key].mean(): .4e}"
                f" sigma  {self.data[key].std(): .4e}"
                f" RMS {rms:.4e}"
            )
