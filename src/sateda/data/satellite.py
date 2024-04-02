import logging
import copy

import numpy as np
import numpy.typing as npt

from sateda.dbconnector import mongo

logger = logging.getLogger(__name__)


class Satellite:
    def __init__(self, mongodb: mongo.MongoDB = None, sat: str = "", series: str = "") -> None:
        self.sat: str = sat
        self.series: str = series
        self.mongodb: mongo.MongoDB = mongodb

        self.time: npt.ArrayLike = np.empty(0, dtype="datetime64[us]")
        self.pos: npt.ArrayLike = np.empty(0)
        self.vel: npt.ArrayLike = np.empty(0)
        self.residual: npt.ArrayLike = np.empty(0)
        self.rac: npt.ArrayLike = np.empty(0)
    
    def copy(self):
        # Using copy.deepcopy() to create a deep copy
        return copy.deepcopy(self)

    def get_postfit(self):
        data = self.mongodb.get_data(
            collection="Measurements",
            state=None,
            sat=[self.sat],
            site=[""],
            series=[self.series],
            keys=["ECI PseudoPos-0-Postfit", "ECI PseudoPos-1-Postfit", "ECI PseudoPos-2-Postfit"],
        )
        self.time = np.asarray(data[0]["t"], dtype="datetime64[us]")
        self.residual = np.empty((len(data[0]["t"]), 3))
        self.residual[:, 0] = data[0]["ECI PseudoPos-0-Postfit"]
        self.residual[:, 1] = data[0]["ECI PseudoPos-1-Postfit"]
        self.residual[:, 2] = data[0]["ECI PseudoPos-2-Postfit"]

    def get_state(self, state="ORBIT"):
        if state == "ORBIT":
            self.get_state_orbit()
        else:
            self.get_state_pos()

    def get_state_orbit(self):
        data = self.mongodb.get_data(
            collection="States",
            state=["ORBIT"],
            sat=[self.sat],
            site=[""],
            series=[self.series],
            keys=["x"],
        )
        self.time = np.empty(len(data[0]["t"]), dtype="datetime64[us]")
        self.pos = np.empty((3, len(data[0]["t"])))
        self.vel = np.empty((3, len(data[0]["t"])))
        self.time = np.asarray(data[0]["t"], dtype="datetime64[us]")
        self.pos = np.asarray(data[0]["x"])[:, :3]
        self.vel = np.asarray(data[0]["x"])[:, 3:]

    def get_state_pos(self):
        """
        todo: add the rate in 1 go.
        """
        data = self.mongodb.get_data(
            collection="States",
            state=["REC_POS"],
            site=[self.sat],
            sat=[""],
            series=[self.series],
            keys=["x"],
        )
        # data_rate = self.mongodb.get_data(
        #     collection="States",
        #     state=["REC_POS_RATE"],
        #     site=[self.sat],
        #     sat=[""],
        #     series=[self.series],
        #     keys=["x"],
        # )
        self.time = np.empty(len(data[0]["t"]), dtype="datetime64[us]")
        self.pos = np.empty((3, len(data[0]["t"])))
        self.vel = np.empty((3, len(data[0]["t"])))
        self.time = np.asarray(data[0]["t"], dtype="datetime64[us]")
        self.pos = np.asarray(data[0]["x"])[:, :3]
        # self.vel = np.asarray(data_rate[0]["x"])[:, 3:]

    def get_rms(self, use_rac=False):
        data = self.residual if not use_rac else self.rac
        rms = np.zeros(4)
        rms[:3] = np.sqrt(np.mean(data**2, axis=0))
        res3d = np.sqrt(np.sum(data**2, axis=1))
        rms[3] = np.sqrt(np.mean(res3d**2))
        return rms

    def get_rac(self):
        r = self.pos / np.linalg.norm(self.pos, axis=1)[:, np.newaxis]
        c = np.cross(self.pos, self.vel)
        c = c / np.linalg.norm(c, axis=1)[:, np.newaxis]
        a = np.cross(c, self.pos)
        a = a / np.linalg.norm(a, axis=1)[:, np.newaxis]
        self.rac = np.empty_like(self.residual)
        self.rac[:, 0] = (r[:-1:3] * self.residual).sum(axis=1)
        self.rac[:, 1] = (a[:-1:3] * self.residual).sum(axis=1)
        self.rac[:, 2] = (c[:-1:3] * self.residual).sum(axis=1)
        return self.get_rms(use_rac=True)

def align_satellites(data1: "Satellite", data2: "Satellite"):
    common_time, in_sat1, in_sat2 = np.intersect1d(data1.time, data2.time, return_indices=True)
    data1.time = common_time
    data2.time = common_time
    data1.pos = data1.pos[in_sat1]
    data2.pos = data2.pos[in_sat2]
    