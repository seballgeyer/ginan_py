"""
Class to read sp3 files
@todo add write methods later.
"""

import logging
from io import StringIO
from typing import Union
import re
import numpy as np
import numpy.typing as npt
import gzip

from sateda.core.time import Time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
class sp3:
    def __init__(self) -> None:
        self.data = {}
        self.header = {}

    @classmethod
    def read(cls, file_or_string: Union[str, StringIO], *args, **kwargs) -> "sp3":
        instance = cls(*args, **kwargs)  # Create an instance of the class
        # Determine if the input is a string path or a StringIO object
        if isinstance(file_or_string, str):
            # Check if the file has a .gz extension to detect compressed files
            is_compressed = file_or_string.endswith('.gz')

            if is_compressed:
                with gzip.open(file_or_string, 'rt') as f:
                    contents = f.read()
            else:
                with open(file_or_string) as f:
                    contents = f.read()
        else:
            # Read from the provided StringIO object
            contents = file_or_string.read()
        header_, data_ = instance._split_header_data(contents)
        instance._read_header(header_)
        instance._parse_data_block(data_)
        return instance

    def merge(self, other: "sp3") -> None:
        """
        Merge two sp3 classes.
        Need to have a loop on data dictionary and merge each satellite together making sure that the time is increasing.
        """
        for sat in other.data.keys():
            if sat not in self.data:
                self.data[sat] = {
                    "time": [],
                    "x": [],
                    "y": [],
                    "z": [],
                }
            for label in ["time", "x", "y", "z"]:
                self.data[sat][label] = np.concatenate((self.data[sat][label], other.data[sat][label]))
            #sort the data along the time value
            sort_idx = np.argsort(self.data[sat]["time"])
            for label in ["time", "x", "y", "z"]:
                self.data[sat][label] = self.data[sat][label][sort_idx]


    def _split_header_data(self, contents: str) -> [str, str]:
        # Use a regular expression to find the first line starting with "*"
        try:
            match = re.search(r'^\*', contents, re.MULTILINE)
            header = contents[:match.start()]
            data = contents[match.start():]
        except:
            logger.error("No header found in sp3 file")
            raise ValueError("No header found in sp3 file")
        return header, data


    def _read_header(self, header: str) -> None:
        # Split the header into lines
        lines = header.splitlines()
        self._parse_header_line1(lines[0])
        self._parse_header_line2(lines[1])
        #find all lines starting with "+ " and parse them
        idx = 2
        while lines[idx].startswith("+ "):
            self._parse_header_line_satellite(lines[idx])
            idx += 1
        #parse the first line

    def _read_data(self, data: str) -> None:
        #split the string into blocks, all start with "*"
        blocks = re.split(r'\n\*', data)
        # Remove empty blocks and add "*" back to the start of each block
        blocks = ['*'+block for block in blocks if block.strip()]
        for block in blocks:
            self._parse_data_block(block)
        print("......")
        for data in self.data:
            self.data[data]["time"] = np.array(self.data[data]["time"])
            self.data[data]["x"] = np.array(self.data[data]["x"])
            self.data[data]["y"] = np.array(self.data[data]["y"])
            self.data[data]["z"] = np.array(self.data[data]["z"])
            print(type(self.data[data]['x']))

    def _parse_data_block(self, block: str) -> None:
        """
        parse the data block
        first line:
        column 4-7: year
        column 9-10: month
        column 12-13: day
        column 15-16: hour
        column 18-19: minute
        column 21-31: second (float)
        other lines:
        column 1: type
        column 2-4: satellite id
        column 5-18: x (float)
        column 19-32: y (float)
        column 33-46: z (float)
        """
        #split the block into lines
        lines = block.splitlines()
        #parse other lines
        for line in lines[0:]:
            if line[0] == "*":
                year = int(line[3:7])
                month = int(line[8:10])
                day = int(line[11:13])
                hour = int(line[14:16])
                minute = int(line[17:19])
                seconds = float(line[20:31])
                microseconds = int(seconds * 1e6)
                seconds = int(seconds)
                microseconds = int(microseconds % 1e6)
                time = Time.from_string(
                    f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{seconds:02d}.{microseconds:06d}")
            else:
                type = line[0]
                if type == "P":
                    temp_satellite = line[1:4].strip()
                    if temp_satellite not in self.data:
                        self.data[temp_satellite] = {}
                        self.data[temp_satellite]["time"] = []
                        self.data[temp_satellite]["x"] = []
                        self.data[temp_satellite]["y"] = []
                        self.data[temp_satellite]["z"] = []
                    self.data[temp_satellite]["time"].append(time)
                    self.data[temp_satellite]["x"].append(float(line[4:18])*1000)
                    self.data[temp_satellite]["y"].append(float(line[18:32])*1000)
                    self.data[temp_satellite]["z"].append(float(line[32:46])*1000)

        for data in self.data:
            self.data[data]["time"] = np.array(self.data[data]["time"])
            self.data[data]["x"] = np.array(self.data[data]["x"])
            self.data[data]["y"] = np.array(self.data[data]["y"])
            self.data[data]["z"] = np.array(self.data[data]["z"])
    def _parse_header_line1(self, line: str) -> None:
        """
        parse the first line of the header
        column 1: #
        column 2: version_letter
        column 3: flag (P or V)
        column 4-7: year
        column 9-10: month
        column 12-13: day
        column 15-16: hour
        column 18-19: minute
        column 21-31: second (float)
        column 33-39: number of epochs
        column 41-45: data used (str)
        column 47-51: coordinate system (str)
        column 53-55: orbit type (str)
        column 57-60: agency (str)

        return everything in the self.header dictionary
        """
        self.header["version_letter"] = line[1]
        self.header["flag"] = line[2]
        year = int(line[3:7])
        month = int(line[8:10])
        day = int(line[11:13])
        hour = int(line[14:16])
        minute = int(line[17:19])
        seconds = float(line[20:31])
        microseconds = int(seconds * 1e6)
        seconds = int(seconds)
        microseconds = int(microseconds % 1e6)
        self.header["start_time"] = np.datetime64(f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{seconds:02d}.{microseconds:06d}" )
        self.header["num_epochs"] = int(line[32:39])
        self.header["data_used"] = line[40:45]
        self.header["coordinate_system"] = line[46:51]
        self.header["orbit_type"] = line[52:55]
        self.header["agency"] = line[56:60]

    def _parse_header_line2(self, line: str) -> None:
        """
        parse the second line of the header
        colunm 1-2: check if "##" raise error
        column 4-7: GPS week
        column 9-23: GPS seconds of week
        column 25-38: epoch interval (float)
        column 40-44: mjd (int)
        column 46-60: fractional day of mjd (float)
        """
        if line[0:2] != "##":
            raise ValueError("Second line of header should start with ##")
        self.header["gps_week"] = int(line[3:7])
        self.header["gps_seconds_of_week"] = float(line[8:23])
        self.header["epoch_interval"] = float(line[24:38])
        self.header["mjd"] = int(line[39:44])
        self.header["fractional_day_of_mjd"] = float(line[45:60])

    def _parse_header_line_satellite(self, line: str) -> None:
        """
        column 4-6: number of satellites (int)
        column 10-12: satellite id (str)
        column 13-15: satellite id (str)
        ...
        column 58-60: satellite id (str)
        append all satellite id into an array, if id is "0" don't happend and stop
        """
        try:
            self.header["nsat"] = int(line[3:6])
        except:
            pass
        if "satellite" not in self.header:
            self.header["satellite"] = []
        for i in range(17):
            temp_name = line[9+i*3:12+i*3]
            temp_name = temp_name.strip()
            if temp_name == "0":
                break
            else:
                self.header["satellite"].append(temp_name)



def sp3_align(data1: sp3, data2: sp3) -> (sp3, sp3):
    """
    function to align 2 sp3 structure together
    it will loop to get all common satellite name, for each of them extract the common time and associated data
    """
    #find the common name in data1.data.keys() and data2.data.keys()
    satellite_names = list(set(data1.data.keys()).intersection(set(data2.data.keys())))
    output_data1 = sp3()
    output_data2 = sp3()
    for sat_name in satellite_names:
        common_time, in_data1, in_data2 = np.intersect1d(data1.data[sat_name]["time"], data2.data[sat_name]["time"], return_indices=True)
        output_data1.data[sat_name] = \
            {
                "time": common_time,
                "x": data1.data[sat_name]["x"][in_data1],
                "y": data1.data[sat_name]["y"][in_data1],
                "z": data1.data[sat_name]["z"][in_data1],
            }
        output_data2.data[sat_name] = \
            {
                "time": common_time,
                "x": data2.data[sat_name]["x"][in_data2],
                "y": data2.data[sat_name]["y"][in_data2],
                "z": data2.data[sat_name]["z"][in_data2],
            }
    return output_data1, output_data2