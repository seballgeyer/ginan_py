import datetime
import logging

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

from sateda.data.measurements import MeasurementArray, Measurements

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Clocks:
    """
    Clock class to handle clock data
    """

    def __init__(
        self,
        data: MeasurementArray = None,
        satlist: list = [],
        series: str = None,
        series_base: str = None,
    ) -> None:
        self.data = data
        self.satlist = satlist
        self.series = series
        self.series_base = series_base

    def process(self) -> None:
        """
        Process the data. process in 2 steps.
        1. locate inside the data vector the two element with the same "sat" name in the self.identifier field.
        2. create a common time vector for the two elements, filling the missing data with Nan.
        """
        result = MeasurementArray()
        print(self.satlist)
        for sat in self.satlist:
            # print("looking for sat", sat)
            ref = None
            est = None
            for data in self.data:
                # print(data.id, self.series, self.series_base)
                if data.id["sat"] == sat and data.id["series"] == self.series:
                    est = data
                if data.id["sat"] == sat and data.id["series"] == self.series_base:
                    ref = data
            if ref is not None and est is not None:
                common_time = np.union1d(ref.epoch, est.epoch)
                common_data1 = np.full_like(common_time, np.nan, dtype="float64")
                common_data2 = np.full_like(common_time, np.nan, dtype="float64")
                # print(ref.data['x'].shape)
                # check if there is a dupllicated epoch in ref.epoch, and remove it, as well as in ref.data['x']
                # Comes from the PEA writting duplicates (last epochs) and inaptitude to deal with it.
                for ts in [ref, est]:
                    _, unique_indices = np.unique(ts.epoch, return_index=True)
                    ts.epoch = ts.epoch[unique_indices]
                    ts.data["x"] = ts.data["x"][unique_indices]
                common_data1[np.isin(common_time, ref.epoch)] = ref.data["x"][:, 0]
                common_data2[np.isin(common_time, est.epoch)] = est.data["x"][:, 0]
                data = {}
                data["x"] = common_data1 - np.nanmean(common_data1) - common_data2 + np.nanmean(common_data2)
                result.append(
                    Measurements(
                        epoch=common_time,
                        data=data,
                        identifier={"sat": sat, "series": self.series},
                    )
                )

        # redo the same ....
        common_time = np.unique(np.concatenate([_result.epoch for _result in result]))
        data = np.full((len(common_time), len(result.arr)), np.nan, dtype="float64")
        for i, _result in enumerate(result):
            data[np.isin(common_time, _result.epoch), i] = _result.data["x"]
        data = np.nanmean(data, axis=1)

        for _result in result:
            _result.data["x"] = _result.data["x"] - data[np.isin(common_time, _result.epoch)]

        return result
