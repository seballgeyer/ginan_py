from io import StringIO
from typing import Union

import numpy as np
import yaml

from sateda.io.grace import gracetime_converter, binary_to_int

gnv_dtype = np.dtype(
    [
        ("gps_time", "datetime64[s]"),
        ("GFO_id", "U1"),
        ("coord_ref", "U1"),
        ("xpos", np.float64),
        ("ypos", np.float64),
        ("zpos", np.float64),
        ("xpos_err", np.float64),
        ("ypos_err", np.float64),
        ("zpos_err", np.float64),
        ("xvel", np.float64),
        ("yvel", np.float64),
        ("zvel", np.float64),
        ("xvel_err", np.float64),
        ("yvel_err", np.float64),
        ("zvel_err", np.float64),
        ("flag", "i4"),
    ]
)


class GraceGNV:
    def __init__(self):
        self.data = 0
        self.yaml_dict = 0

    def read(self, file_or_string: Union[str, StringIO]) -> None:
        if isinstance(file_or_string, str):
            with open(file_or_string) as f:
                contents = f.read()
        else:
            contents = file_or_string.read()
        yaml_lines = contents.split("# End of YAML header")[0]
        data_lines = contents.split("# End of YAML header")[1].strip()
        self.yaml_dict = yaml.safe_load(yaml_lines)
        self.data = np.loadtxt(
            StringIO(data_lines),
            dtype=gnv_dtype,
            converters={0: gracetime_converter, 15: binary_to_int},
        )
