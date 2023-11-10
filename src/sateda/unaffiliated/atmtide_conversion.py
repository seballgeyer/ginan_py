import numpy as np
from netCDF4 import Dataset
import sys


def helmert_fit(x, p):
    """
    Built the design matrix to determine the 7 parameters helmert parameter for going from vector x to vector p. using small angle approximation
    x and p are of dimension (3, ntimes) where ntimes is the number of epochs
    """
    D = np.zeros((3 * x.shape[1], 7))
    for i in range(x.shape[1]):
        D[3 * i : 3 * i + 3, 0] = 1
        D[3 * i : 3 * i + 3, 1] = x[:, i]
        D[3 * i : 3 * i + 3, 2] = -p[1, i]
        D[3 * i : 3 * i + 3, 3] = p[0, i]
        D[3 * i : 3 * i + 3, 4] = 0
        D[3 * i : 3 * i + 3, 5] = -p[2, i]
        D[3 * i : 3 * i + 3, 6] = p[1, i]


a = np.loadtxt("s1_s2_def_ce.dat")

lon = a[:, 0].reshape(361, 181)
lat = a[:, 1].reshape(361, 181)

lon = lon[:, 0]
lat = lat[0, :]
data = a[:, 2:]  # .reshape(12,361,181)
# Swap first index of data with the followin mapint
# idx 0 = idx 0
# idx 1 = idx 1
# idx 2 = idx 8
# idx 3 = idx 9
# idx 4 = idx 4
# idx 5 = idx 5
# idx 6 = idx 2
# idx 7 = idx 3
# idx 8 = idx 10
# idx 9 = idx 11
# idx 10 = idx 6
# idx 11 = idx 7
mapping = [0, 1, 8, 9, 4, 5, 2, 3, 10, 11, 6, 7]
a = np.zeros((12, 361, 181))
print(data[:, 0])
for i in range(12):
    a[i, :, :] = (data[:, mapping[i]] / 1000.0).reshape(361, 181)
# print(a[0])
# exit(0)
with Dataset("atmtide.nc", "w") as nc:
    nc.createDimension("lat", len(lat))
    nc.createDimension("lon", len(lon))
    nc.createDimension("number_waves", 2)
    nc.createDimension("nwaves", 12)
    nc.wave_name = "S1, S2"
    latV = nc.createVariable("lat", float, ("lat",))
    lonV = nc.createVariable("lon", float, ("lon",))
    waves_l = nc.createVariable("waves", float, ("nwaves", "lat", "lon"))
    latV[:] = lat[::-1]
    lonV[:] = lon
    for i in range(12):
        waves_l[i, :, :] = a[i, :, ::-1].transpose()
