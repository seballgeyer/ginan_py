
from io import StringIO
from typing import Union

import numpy as np
from numpy.lib.recfunctions import drop_fields, join_by

from ginan.io.sinex.definitions import read_func




class Sinex():
    def __init__(self) -> None:
        self.blocks = {}

    def read(self, file_or_string: Union[str,StringIO]) -> None:
        if isinstance(file_or_string, str):
            with open(file_or_string) as f:
                self.read_file(f)
        else:
            self.read_file(file_or_string)

    def read_file(self, f: StringIO) -> None:
        block_name = None
        block_data = {}
        for line in f:
            print(line)
            if line.startswith("+"):
                if block_name:
                    self.blocks[block_name] = block_data

                block_name = line[1:].strip()
                block_data = {}
            elif line.startswith("-"):
                self.blocks[block_name] = block_data
                block_name = None
            else:
                if block_name in read_func:
                    func = read_func[block_name]
                    block_data.update(func(f))
                    self.blocks[block_name] = block_data
                    block_name = None
                else:
                    print(f"no parser for block {block_name}")

    def merge(self):
        result = {}
        for subdic_name, subdict_data in self.blocks.items():
            for svn, subsubdcit  in subdict_data.items():
                if svn not in result:
                    result[svn] = {}
                result[svn][subdic_name] = subsubdcit
        return result

import yaml


if __name__ == "__main__":
    s = Sinex()
    s.read("scratch/igs_satellite_metadata_2203_plus.snx")
    import pprint
    for s1 in s.blocks:
        print(s1)
        pprint.pprint(s.blocks[s1])
    d = s.merge()
    # import pprint
    pprint.pprint(d)
    # print(yaml.safe_load(yaml.dump(d)))
