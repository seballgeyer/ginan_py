from io import StringIO
from typing import Union

import numpy as np
import yaml

from sateda.io.grace import gracetime_converter, binary_to_int

acc_dtype = np.dtype(
    [
        ("gps_time", "datetime64[s]"),
        ("GFO_id", "U1"),
        ("lin_accl_x", np.float64),
        ("lin_accl_y", np.float64),
        ("lin_accl_z", np.float64),
        ("ang_accl_x", np.float64),
        ("ang_accl_y", np.float64),
        ("ang_accl_z", np.float64),
        ("acl_x_res", np.float64),
        ("acl_y_res", np.float64),
        ("acl_z_res", np.float64),
        ("flag", "i4"),
    ]
)

class GraceACC:
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
            dtype=acc_dtype,
            converters={0: gracetime_converter, 11: binary_to_int},
        )
