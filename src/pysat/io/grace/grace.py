import datetime

import numpy as np
from typing import Union

from pysat.data.satellite import satellite


class grace(satellite):
    def __init__(self, date: Union[int, datetime, np.datetime64]):
        self.date: np.datetime64 = date

    @property
    def date(self) -> np.datetime64:
        return self._date

    @date.setter
    def date(self, value: Union[int, datetime, np.datetime64]) -> None:
        if isinstance(value, (int, np.integer)):
            self._date = np.datetime64(datetime(2000, 1, 1)) + np.timedelta64(value, "s")
        elif isinstance(value, datetime):
            self._date = np.datetime64(value)
        elif isinstance(value, np.datetime64):
            self._date = value
        else:
            raise ValueError("Invalid date format")
