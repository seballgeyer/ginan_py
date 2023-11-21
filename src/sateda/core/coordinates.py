import erfa as erfa
import numpy as np

from sateda.core.time import Time, TimeSystem

DX06 = 0.1750e-3 / 3600 * np.pi / 180
DY06 = -0.2259e-3 / 3600 * np.pi / 180

DX00 = 0.1725e-3 / 3600 * np.pi / 180
DY00 = -0.2650e-3 / 3600 * np.pi / 180


class Eop:
    def __init__(self, time: Time) -> None:
        self.xp = 0
        self.yp = 0
        self.dut1 = 0
        self.dlod = 0
        self.ut1_utc = 0
        self.lod = 0
        self.X = 0
        self.Y = 0
        self.s = 0
        self.era = 0
        self.gmst = 0
        self.gast = 0
        self.time = time

    def iau2000(self):
        self.X, self.Y, self.s = erfa.xys00a(*self.time.to_tt().to_jd())
        self.X += DX00
        self.Y += DY00
        ut1, ut2 = self.time.to_utc().to_jd()
        ut2 += self.ut1_utc / 86400
        self.era = erfa.era00(ut1, ut2)
        self.iau_rotations()

    def iau2006(self):
        self.X, self.Y = erfa.xy06(*self.time.to_tt().to_jd())
        self.s = erfa.s06(*self.time.to_tt().to_jd(), self.X, self.Y)
        self.X += DX06
        self.Y += DY06
        ut1, ut2 = self.time.to_utc().to_jd()
        ut2 += self.ut1_utc / 86400
        self.era = erfa.era00(ut1, ut2)
        self.iau_rotations()

    def iau_rotations(self):
        r2ci = erfa.c2ixys(self.X, self.Y, self.s)
        rc2ti = erfa.cr(r2ci)
        rc2ti = erfa.rz(self.era, rc2ti)
        rpom = erfa.pom00(self.xp, self.yp, erfa.sp00(*self.time.to_tt().to_jd()))
        self.rot = erfa.rxr(rpom, rc2ti)

    def generate_rotation(self) -> np.array:
        # c2ixuz
        r2 = self.X * self.X + self.Y * self.Y
        e = np.arctan2(self.Y, self.X) if r2 > 0 else 0
        d = np.arctan(np.sqrt(r2 / (1 - r2)))

        rc2i = np.eye(3)
        rc2i = rc2i @ self._rz(e)
        rc2i = rc2i @ self._ry(d)
        rc2i = rc2i @ self._rz(-(e + self.s))
        # print(rc2i)
        return rc2i

    def _rz(self, angle: float) -> np.array:
        return np.array([[np.cos(angle), np.sin(angle), 0], [-np.sin(angle), np.cos(angle), 0], [0, 0, 1]])

    def _ry(self, angle: float) -> np.array:
        return np.array([[np.cos(angle), 0, -np.sin(angle)], [0, 1, 0], [np.sin(angle), 0, np.cos(angle)]])
