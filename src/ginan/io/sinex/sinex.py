
from io import StringIO
from typing import Union

import numpy as np
from numpy.lib.recfunctions import drop_fields

from ginan.io.sinex.definitions import sinex_def




class Sinex():
    def __init__(self) -> None:
        self.blocks = {}

    def read(self, file_or_string: Union[str,StringIO]) -> None:
        if isinstance(file_or_string, str):
            with open(file_or_string) as f:
                contents = f.readlines()
        else:
            contents = file_or_string.readlines()

        blocks = {}
        current_block = None
        for line in contents:
            if line.startswith("+"):
                label = line[1:].strip()
                print("find", label)
                current_block = []
            elif line.startswith("-"):
                if current_block and label in sinex_def:
                    print(label)
                    self.blocks [label] = np.genfromtxt(current_block,
                                                  dtype=sinex_def[label]['dtype'], comments="*", delimiter=sinex_def[label]['sep'], converters=sinex_def[label]['conv'])
                    self.blocks [label] = drop_fields(self.blocks [label],
                                                [name for name, _ in self.blocks [label].dtype.descr if name.startswith('_')])
                    current_block = None
                elif current_block and label not in sinex_def:
                    print(f"block {label} doesn't have a parser yet... skipping")
            elif current_block is not None:
                current_block.append(line)

        for  block in self.blocks:
            print("====")
            print(block)
            print(self.blocks[block])
            print("++++")
