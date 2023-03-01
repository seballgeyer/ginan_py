from io import StringIO
from typing import Union
import logging

import numpy as np
from numpy.lib.recfunctions import drop_fields, join_by

from pysat.io.sinex.definitions import read_func

logger = logging.getLogger(__name__)


class Sinex:
    def __init__(self) -> None:
        self.blocks = {}

    def read(self, file_or_string: Union[str, StringIO]) -> None:
        if isinstance(file_or_string, str):
            with open(file_or_string) as f:
                self.read_file(f)
        else:
            self.read_file(file_or_string)

    def read_file(self, f: StringIO) -> None:
        block_name = None
        block_data = {}
        for line in f:
            if line.startswith("+"):
                if block_name:
                    self.blocks[block_name] = block_data

                block_name = line[1:].strip()
                block_data = {}
            elif line.startswith("-"):
                self.blocks[block_name] = block_data
                block_name = None
            else:
                if block_name:
                    if block_name in read_func:
                        func = read_func[block_name]
                        block_data.update(func(f))
                        self.blocks[block_name] = block_data
                        block_name = None
                    else:
                        logger.info(f"no parser for block {block_name}")
                        func = read_func["None"]
                        block_name = None

    def merge(self):
        result = {}
        for subdic_name, subdict_data in self.blocks.items():
            # todo: there is a None block created somewhere.
            if subdic_name:
                name = subdic_name.split("/")[-1].lower()
                for svn, subsubdict in subdict_data.items():
                    if svn not in result:
                        result[svn] = {}
                    # subsubdict.pop("comment")
                    result[svn][name] = subsubdict
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

    print(yaml.dump(d))
