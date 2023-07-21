"""
    class dealing with interpolation of the Earth Orientation Parameters (EOP)
"""

import numpy as np
from scipy.interpolate import lagrange
from numpy.polynomial.polynomial import Polynomial


class EOP:
    def __init__(self) -> None:
        #define EOP variables (default type is numpy array (float))
        self.mjd = np.array([])
        self.x = np.array([])
        self.y = np.array([])
        self.ut1_utc = np.array([])
        self.lod = np.array([])
        self.dX = np.array([])
        self.dY = np.array([])        
        pass
    
    def read_C04(self, filename: str) -> None:
        """
        read_C04 _summary_

        :param str filename: path to the C04 file.
        """
        with open(filename, "r") as f:
            header_lines = 0
            for line in f:
                if line[0:4].isdigit():
                    break
                header_lines = header_lines + 1
            f.seek(0)
            self.C04 = np.genfromtxt(f, skip_header=header_lines)
            self.mjd = self.C04[:, 3]
            self.x = self.C04[:, 4]
            self.y = self.C04[:, 5]
            self.ut1_utc = self.C04[:, 6]
            self.lod = self.C04[:, 7]
            self.dX = self.C04[:, 8]
            self.dY = self.C04[:, 9]
    
    def interpolate_lagrange(self, mjd: float, degree: int) -> None:
        #interpolate the EOP variables to the given mjd using a polynomial interpolation of degree defined by the user
        locate = np.searchsorted(self.mjd, mjd, side='left')
        mjd_ = self.mjd[locate-degree:locate+degree]
        mjd_ = mjd_ - mjd
        result = np.zeros((6,))
        for i, data in enumerate([self.x, self.y, self.ut1_utc, self.lod, self.dX, self.dY]):
            poly = lagrange(mjd_, data[locate-degree:locate+degree])
            result[i] = Polynomial(poly.coef[::-1])(0)
        return result
    
    def interpolate_linear(self, mjd: float):
        locate = np.searchsorted(self.mjd, mjd, side='left')
        result = np.zeros((6,))
        for i, data in enumerate([self.x, self.y, self.ut1_utc, self.lod, self.dX, self.dY]):
            result[i] = np.interp(mjd, self.mjd[locate-1:locate+1], data[locate-1:locate+1])
        return result
    
    def interpolate_neville(self, mjd, degree):
        locate = np.searchsorted(self.mjd, mjd, side='left')
        center = locate - degree // 2  # Calculate the center index
        result = np.zeros((6,))
        for i, data in enumerate([self.x, self.y, self.ut1_utc, self.lod, self.dX, self.dY]):
            n = degree + 1
            Q = np.zeros((n, n))
            Q[:, 0] = data[center : center + n]
            for j in range(1, n):
                for k in range(n - j):
                    Q[k, j] = ((mjd - self.mjd[center + k]) * Q[k + 1, j - 1] - (mjd - self.mjd[center + k + j]) * Q[k, j - 1]) \
                                / (self.mjd[center + k + j] - self.mjd[center + k])
            result[i] = Q[0, degree]
        return result
    
                
            
if __name__ == "__main__":
    eop = EOP()
    eop.read_C04('eopc04_14_IAU2000.62-now.txt')
    print(eop.mjd)
    date = np.arange(37667.25, 37670.75, 1/(24*60))
    lagrange_data = np.zeros((len(date), 6))
    linear_data = np.zeros((len(date), 6))
    neuville_data = np.zeros((len(date), 6))
    for i, d in enumerate(date):
        # print(d)
        lagrange_data[i, :] = eop.interpolate_lagrange(d, 3)
        neuville_data[i, :] = eop.interpolate_neville(d, 3)
        linear_data[i, :] = eop.interpolate_linear(d)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(nrows=6, ncols=2, sharex=True)
    for i in range(6):
        ax[i,0].plot(date, lagrange_data[:, i])
        ax[i,0].plot(date, neuville_data[:, i])
        ax[i,1].plot(date, lagrange_data[:, i] - neuville_data[:, i])

    plt.show()