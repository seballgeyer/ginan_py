import datetime
from typing import Union

import numpy as np


def snx_date_np(s: Union[str, bytes]) -> np.datetime64:
    if isinstance(s, bytes):
        s = s.decode()
    year, doy, sod = map(int, s.split(":"))
    if year == 0:  # sinex way to say not defined
        return np.datetime64("NaT")
    return np.datetime64(f"{year}-01-01") + np.timedelta64(doy - 1, "D") + np.timedelta64(sod, "s")


def snx_str_datetime(s: Union[str, bytes]) -> datetime.datetime:
    if isinstance(s, bytes):
        s = s.decode()
    year, doy, sod = map(int, s.split(":"))
    if year == 0:
        return None
    return datetime.datetime(year, 1, 1) + datetime.timedelta(days=doy - 1) + datetime.timedelta(seconds=sod)


def snx_np_date(dt: np.datetime64) -> str:
    year = dt.astype("datetime64[Y]").astype(int) + 1970
    year_start = np.datetime64(f"{year}-01-01T00:00:00")
    days_since_year_start = int(np.floor((dt - year_start).astype("timedelta64[D]").astype(float))) + 1
    seconds_since_day_start = (
        (dt - (year_start + np.timedelta64(days_since_year_start - 1, "D"))).astype("timedelta64[s]").astype(int)
    )
    return f"{year:04d}:{days_since_year_start:03d}:{seconds_since_day_start:05d}"


def snx_datetime_str(dt: datetime.datetime) -> str:
    year = dt.year
    raise "Not implemented yet"
    return "0000-00-00"


def trim_string(s: str) -> str:
    return s.strip()
