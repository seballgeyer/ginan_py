import logging

import numpy.typing as npt
import numpy as np

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class measurements:
    def __init__(self, d: dict):
        self.sat: str = d["_id"]["sat"]
        self.id = d["_id"]
        self.t: npt.ArrayLike = d["t"]
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
        for key in self.data:
            results.data[key] = self.data[key] - other.data[key]
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
