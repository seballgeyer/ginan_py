import numpy.typing as npt
import numpy as np

import matplotlib.pyplot as plt


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

    def plot(self, ax: plt.Axes):
        for key in self.data:
            ax.plot(self.t, self.data[key])

    def stats(self):
        for key in self.data:
            print(f"{self.id}, {key} {self.data[key].mean(): .4e} sigma  {self.data[key].std(): .4e}")
