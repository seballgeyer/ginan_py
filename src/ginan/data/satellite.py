import logging

import numpy as np
import numpy.typing as npt

from ginan.dbconnector import mongo

logger = logging.getLogger(__name__)


class satellite:
    def __init__(self, mongodb: mongo.MongoDB, sat: str = "", series: str = "") -> None:
        self.sat: str = sat
        self.series: str = series
        self.mongodb: mongo.MongoDB = mongodb

        self.time: npt.ArrayLike = np.empty(0)
        self.pos: npt.ArrayLike = np.empty(0)
        self.vel: npt.ArrayLike = np.empty(0)
        self.residual: npt.ArrayLike = np.empty(0)

    def get_postfit(self):
        data = self.mongodb.get_data(collection='Measurements', state=None, sat=[self.sat], site=[''], series=self.series,
                                     keys=["PseudoPos0-Postfit", "PseudoPos1-Postfit", "PseudoPos2-Postfit"])
        self.time = np.asarray(data[0]['t'], dtype='datetime64[us]')
        self.residual = np.empty((3, len(data[0]['t'])))
        self.residual[0] = data[0]['PseudoPos0-Postfit']
        self.residual[1] = data[0]['PseudoPos1-Postfit']
        self.residual[2] = data[0]['PseudoPos2-Postfit']

    def get_state(self):
        data = self.mongodb.get_data(collection='States', state="SAT_POS", sat=[self.sat], site=[''], series=self.series,
                                     keys=["x"])
        data_rate = self.mongodb.get_data(collection='States', state="SAT_POS_RATE", sat=[self.sat], site=[''], series=self.series,
                                     keys=["x"])
        self.pos = np.empty((3, len(data[0]['t'])))
        self.vel = np.empty((3, len(data[0]['t'])))
        self.pos = np.asarray(data[0]['x'])
        self.vel = np.asarray(data_rate[0]['x'])

    def get_rms(self):
        rms = np.zeros(4)
        rms [:3] = np.sqrt(np.mean(self.residual**2, axis=1))
        res3d = np.sqrt(np.sum(self.residual**2, axis=0))
        rms [3] = np.sqrt(np.mean(res3d**2))
        return rms

    def rac(self):
        r = self.pos / np.linalg.norm(self.pos, axis=1)[:, np.newaxis]
        c = np.cross(self.pos, self.vel)
        c = c / np.linalg.norm(c, axis=1)[:, np.newaxis]
        a = np.cross(c, self.pos)
        a = a / np.linalg.norm(a, axis=1)[:, np.newaxis]
        print(r)



if __name__=="__main__":
    for db_name in ["IGS_a", "IGS_b", "IGS_c"]:
        for sat in ["G01", "G02"]:
            db = mongo.MongoDB(url="127.0.0.1", data_base=db_name)
            satG01 = satellite(db, sat=sat)
            satG01.get_postfit()
            rms = satG01.get_rms()
            print(f"{db_name} {sat}   {np.array2string(rms[:3], precision=6, floatmode='fixed')}  => {rms[3]:.6f}")
            satG01.get_state()
            satG01.rac()



