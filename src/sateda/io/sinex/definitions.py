from sateda.io.sinex.utils import trim_string, snx_str_datetime


def _read_sat_identifier(f):
    block_data = {}
    for line in f:
        if block_edge(line):
            break
        if not line.startswith("*"):
            _svn = trim_string(line[1:5])
            _cospar = trim_string(line[5:16])
            _satCat = int(line[17:23])
            _block = trim_string(line[23:39])
            _comment = trim_string(line[39:])
            if _svn not in block_data:
                block_data[_svn] = {}
            block_data[_svn] = {
                "cospar": _cospar,
                "satCat": _satCat,
                "block": _block,
                "comment": _comment,
            }
    return block_data


def _read_sat_txpower(f):
    block_data = {}
    for line in f:
        if block_edge(line):
            break
        if not line.startswith("*"):
            _svn = trim_string(line[1:5])
            _startdate = snx_str_datetime(line[5 : 14 + 5])
            _enddate = snx_str_datetime(line[20 : 14 + 20])
            _power = float(line[36:41])
            _comment = trim_string(line[41:])
            if _svn not in block_data:
                block_data[_svn] = {}
            block_data[_svn] = {_startdate: {"endDate": _enddate, "power": _power, "comment": _comment}}
    return block_data


def _read_sat_yaw(f):
    block_data = {}
    for line in f:
        if block_edge(line):
            break
        if not line.startswith("*"):
            _svn = trim_string(line[1:5])
            _startdate = snx_str_datetime(line[5 : 14 + 5])
            _enddate = snx_str_datetime(line[20 : 14 + 20])
            _ub = trim_string(line[35 : 6 + 35])
            _rate = float(line[41 : 41 + 8])
            _comment = trim_string(line[49:])
            if _svn not in block_data:
                block_data[_svn] = {}
            block_data[_svn] = {
                _startdate: {
                    "endDate": _enddate,
                    "ub": _ub,
                    "rate": _rate,
                    "comment": _comment,
                }
            }
    return block_data


def _read_sat_mass(f):
    block_data = {}
    for line in f:
        if block_edge(line):
            break
        if not line.startswith("*"):
            # reading...
            _svn = trim_string(line[1:5])
            _startdate = snx_str_datetime(line[5 : 14 + 5])
            _enddate = snx_str_datetime(line[20 : 14 + 20])
            _mass = float(line[35 : 35 + 9])
            _comment = trim_string(line[45:])
            if _svn not in block_data:
                block_data[_svn] = {}
            block_data[_svn].update({_startdate: {"endDate": _enddate, "mass": _mass, "comment": _comment}})
    return block_data


def _read_sat_prn(f):
    block_data = {}
    for line in f:
        if block_edge(line):
            break
        if not line.startswith("*"):
            _svn = trim_string(line[1:5])
            _startdate = snx_str_datetime(line[6 : 14 + 6])
            _enddate = snx_str_datetime(line[20 : 14 + 20])
            _prn = trim_string(line[35 : 35 + 4])
            _comment = trim_string(line[39:])
            if _svn not in block_data:
                block_data[_svn] = {}
            block_data[_svn].update({_startdate: {"startDate": _startdate, "endDate": _enddate, "prn": _prn, "comment": _comment}})
    return block_data


def _read_none(f) -> None:
    block_data = {}
    for line in f:
        if block_edge(line):
            break
    return


def block_edge(line: str) -> bool:
    return line.startswith("+") or line.startswith("-")


read_func = {
    "SATELLITE/MASS": _read_sat_mass,
    "SATELLITE/PRN": _read_sat_prn,
    "SATELLITE/YAW_BIAS_RATE": _read_sat_yaw,
    "SATELLITE/TX_POWER": _read_sat_txpower,
    "SATELLITE/IDENTIFIER": _read_sat_identifier,
    "None": _read_none,
}
