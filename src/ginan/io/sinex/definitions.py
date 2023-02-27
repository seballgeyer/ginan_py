import numpy as np

from ginan.io.sinex.utils import trim_string, snx_date_np

sinex_def = {}


# SATELLITE/IDENTIFIER
sinex_def['SATELLITE/IDENTIFIER']=\
    {
        'dtype': np.dtype([
            ('_0', 'U1'),
            ('svn', 'U4'),
            ('_1', 'U1'),
            ('cospar_id', 'U9'),
            ('_2', 'U1'),
            ('SatCat', int),
            ('_3', 'U1'),
            ('block', 'U15'),
            ('_4', 'U1'),
            ('comment', 'U41')
        ])
        ,
        'sep': [1, 4, 1, 9, 1, 6, 1, 15, 1, 41],
        'conv': {1: trim_string, 3: trim_string, 7: trim_string, 9: trim_string}
    }


#SATELLITE/PRN
sinex_def['SATELLITE/PRN']= \
    {
        'dtype': np.dtype([
            ('_0', 'U1'),
            ('svn', 'U4'),
            ('_1', 'U1'),
            ('valid_from', 'datetime64[s]'),
            ('_2', 'U1'),
            ('valid_to', 'datetime64[s]'),
            ('_3', 'U1'),
            ('prn', 'U3'),
            ('_4', 'U1'),
            ('comment', 'U41')
        ])
        ,
        'sep': [1, 4, 1, 14, 1, 14, 1, 3, 1, 40],
        'conv': {1: trim_string, 3: snx_date_np, 5:snx_date_np, 7: trim_string, 9: trim_string}
    }

sinex_def['SATELLITE/FREQUENCY_CHANNEL'] = \
    {
        'dtype': np.dtype([
            ('_0', 'U1'),
            ('svn', 'U4'),
            ('_1', 'U1'),
            ('valid_from', 'datetime64[s]'),
            ('_2', 'U1'),
            ('valid_to', 'datetime64[s]'),
            ('_3', 'U1'),
            ('chn', int),
            ('_4', 'U1'),
            ('comment', 'U39')
        ])
        ,
        'sep': [1, 4, 1, 14, 1, 14, 1, 3, 1, 39],
        'conv': {1: trim_string, 3: snx_date_np, 5: snx_date_np, 7: trim_string, 9: trim_string}
    }

sinex_def['SATELLITE/MASS'] = \
    {
        'dtype': np.dtype([
            ('_0', 'U1'),
            ('svn', 'U4'),
            ('_1', 'U1'),
            ('valid_from', 'datetime64[s]'),
            ('_2', 'U1'),
            ('valid_to', 'datetime64[s]'),
            ('_3', 'U1'),
            ('mass', float),
            ('_4', 'U1'),
            ('comment', 'U39')
        ])
        ,
        'sep': [1, 4, 1, 14, 1, 14, 1, 9, 1, 34],
        'conv': {1: trim_string, 3: snx_date_np, 5: snx_date_np, 9: trim_string}
    }
