
from io import StringIO
from typing import Union

import numpy as np
from numpy.lib.recfunctions import drop_fields



dtype={
    'SATELLITE/IDENTIFIER':
        np.dtype([
            ('_0', 'U1'),
            ('svn', 'U4'),
            ('_1', 'U1'),
            ('cospar_id', 'U9'),
            ('_2', 'U1'),
            ('SatCat', np.int32),
            ('_3', 'U1'),
            ('block','U15'),
            ('_4', 'U1'),
            ('comment', 'U41')
        ])
}

sep={
    'SATELLITE/IDENTIFIER':[ 1, 4, 1, 9,1,  6,1,  15,1,  41]
}

def trim_string(s):
    return s.strip()

conv={
    'SATELLITE/IDENTIFIER':{1:trim_string, 3:trim_string, 7:trim_string, 9:trim_string}
}
class Sinex():
    def __init__(self) -> None:
        self.block = {}

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
                current_block = []
            elif line.startswith("-"):
                if current_block is not None and label in dtype:
                    blocks[label] = np.genfromtxt(current_block,
                                                  dtype=dtype[label], comments="*", delimiter=sep[label], converters=conv[label])
                    current_block = None
            elif current_block is not None:
                current_block.append(line)

        #
        # return blocks
        #
        # blocks = {}
        # current_block = []
        # current_label = None
        #
        # for line in contents:
        #     if line.startswith('+'):
        #         if current_block:
        #             blocks[current_label] = current_block
        #         current_label = line[1:].strip().replace("/","_")
        #         current_block = []
        #     elif line.startswith('-'):
        #         current_block.append(line)
        #     else:
        #         current_block.append(line)

        # if current_block:
        #     print(current_block)
        #     if current_label in dtype:
        #         print('parsing ', curr)
        #         blocks[current_label] = current_block
        #         blocks[current_label] = np.genfromtxt(current_block,
        #                                           dtype=dtype[current_label])


        for  block in blocks:
            print("====")
            blocks[block] = drop_fields(blocks[block], [name for name, _ in blocks[block].dtype.descr if name.startswith('_')])

            print(block)
            print(blocks[block])
            print("++++")
