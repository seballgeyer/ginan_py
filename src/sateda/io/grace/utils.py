import numpy as np


def gracetime_converter(s):
    return np.datetime64("2000-01-01T12:00:00") + np.timedelta64(int(s), "s")


def binary_to_int(bin_str):
    return int(bin_str, 2)
