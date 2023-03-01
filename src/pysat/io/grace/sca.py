import yaml
import numpy as np
from io import StringIO
from typing import Union

from pysat.io.grace import gracetime_converter, binary_to_int


sca_dtype = np.dtype(
    [
        ("gps_time", "datetime64[s]"),
        ("GFO_id", "U1"),
        ("sca_id", np.int32),
        ("quaternioni", np.float64),
        ("quaternionj", np.float64),
        ("quaternionk", np.float64),
        ("quaternionl", np.float64),
        ("quality", np.float64),
        ("flag", "i4"),
    ]
)


class GraceSCA:
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
            StringIO(data_lines), dtype=sca_dtype, converters={0: gracetime_converter, 8: binary_to_int}
        )
