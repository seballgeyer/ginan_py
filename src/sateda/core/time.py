import logging

import numpy as np
import enum

logger = logging.getLogger(__name__)

class TimeSystem(enum.Enum):
    """Enum for time systems"""
    UTC = "UTC"
    TAI = "TAI"
    TT = "TT"
    GPS = "GPS"
    UNKNOWN = None

class Time:
    """
    Class for time handling
    @todo Extend to handle different time systems and leap seconds
    """

    def __init__(self, dt64=np.datetime64("1970-01-01T00:00:00"), timesystem=TimeSystem.GPS):
        self.timesystem = timesystem
        self.leapsec = 33
        self.time = dt64

        self._convert_to_gps()

    @classmethod
    def from_string(cls, time_string, timesystem=TimeSystem.GPS):
        gps_time = np.datetime64(time_string)
        return cls(gps_time, timesystem)

    @classmethod
    def from_datetime64(cls, dt64, timesystem=TimeSystem.GPS):
        return cls(dt64, timesystem)

    @classmethod
    def from_components(cls, year, month, day, hour=0, minute=0, second=0, microsecond=0, timesystem=TimeSystem.GPS):
        gps_time = np.datetime64(f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{microsecond:06d}")
        return cls(gps_time, timesystem)

    def __str__(self):
        return f"{self.time} {self.timesystem.value}"

    def __repr__(self):
        return f"{self.time} {self.timesystem.value}"

    def _convert_to_gps(self):
        if self.timesystem == TimeSystem.UTC:
            self.time += np.timedelta64( self.leapsec - 19, 's')
            self.timesystem = TimeSystem.GPS
        pass
        # raise ValueError("Conversion to GPS time is not implemented yet")

    def _convert_from_gps(self):
        if self.timesystem == TimeSystem.UTC:
            self.time -= np.timedelta64( 18, 's')
        elif self.timesystem == TimeSystem.TAI:
            self.time += np.timedelta64(19, 's')
        elif self.timesystem == TimeSystem.TT:
            self.time += np.timedelta64(51184, 'ms')
        else:
            logger.debug("Time system is not known, no conversion is done")

    def to_utc(self):
        new_time = Time()
        new_time.time = self.time - np.timedelta64(self.leapsec - 19, 's')
        new_time.timesystem = TimeSystem.UTC
        return new_time

    def to_tai(self):
        new_time = Time()
        new_time.time = self.time + np.timedelta64( 19, 's')
        new_time.timesystem = TimeSystem.TAI
        return new_time

    def to_tt(self):
        new_time = Time()
        new_time.time = self.time + np.timedelta64( 19, 's')  + np.timedelta64(32184, 'ms')
        new_time.timesystem = TimeSystem.TT
        return new_time

    def to_mjd(self):
        #compute the mjd in 2 parts, first the integer part, then the fractional part
        mjd_int = self._compute_mjd_int()
        mjd_frac = self._compute_mjd_frac()
        return (mjd_int,  mjd_frac)
        # return (self.time - np.datetime64('1858-11-17T00:00:00')) / np.timedelta64(1, 'D')

    def _compute_mjd_int(self):
        return np.floor((self.time - np.datetime64('1858-11-17T00:00:00')) / np.timedelta64(1, 'D'))

    def _compute_mjd_frac(self):
        seconds_of_day = (self.time - np.datetime64(self.time.astype('datetime64[D]'))).astype('timedelta64[ns]').astype(int)
        print(seconds_of_day/1e9)
        return seconds_of_day/86400e9

    def to_jd(self):
        mjd, mjd_f = self.to_mjd()
        return mjd + 2400000.5, mjd_f