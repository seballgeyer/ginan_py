import numpy as np


def snx_date_np(s: str) -> np.datetime64:
    year_str, day_str, second_str = s.split(':')
    year = int(year_str)
    day = int(day_str)
    second = int(second_str)
    seconds_since_year_start = (day - 1) * 24 * 60 * 60 + second
    year_start = np.datetime64(f"{year}-01-01T00:00:00")
    return year_start + np.timedelta64(seconds_since_year_start)

def snx_np_date(dt: np.datetime64) -> str:
    year = dt.astype('datetime64[Y]').astype(int) + 1970
    year_start = np.datetime64(f"{year}-01-01T00:00:00")
    days_since_year_start = (dt - year_start).astype(int) // (24 * 60 * 60 * 10**9) + 1
    seconds_since_day_start = (dt - year_start).astype(int) // (10**9) % (24 * 60 * 60)
    return f"{year:04d}:{days_since_year_start:03d}:{seconds_since_day_start:05d}"