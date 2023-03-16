import logging
import argparse

import matplotlib.pyplot as plt
import numpy as np

from pysat.data.measurements import Measurements
from pysat.dbconnector import mongo
from pysat.utils.patterns import match_patterns, generate_list
from pysat.utils.common import find_common
import sys


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            return record.getMessage()
        else:
            return f"{record.levelname} > {record.getMessage()}"


logger = logging.getLogger("main")
formatter = CustomFormatter()
logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


def plot_measurements(args):
    db1 = mongo.MongoDB(url=args.db1, data_base=args.coll1, port=args.port1)
    db2 = mongo.MongoDB(url=args.db2, data_base=args.coll2, port=args.port2)

    data = []
    for i, db in enumerate([db1, db2]):
        sites = generate_list(args.site, db.mongo_content["Site"])
        sats = generate_list(args.sat, db.mongo_content["Sat"])

        keys = {k: k for k in args.field}
        dd = db.get_data("Measurements", sat=sats, site=sites, state=None, series="", keys=keys)
        data.append([])
        for d in dd:
            try:
                data[-1].append(Measurements(d))
                logger.info(f"Find {data[-1][-1].id}")
            except ValueError as e:
                logger.warning(d["_id"], "doesn't have values")

    common, diff1, diff2 = find_common(data[0], data[1])
    for d in diff1:
        logger.warning(f"{data[0][d].id} not in second db")
    for d in diff2:
        logger.warning(f"{data[1][d].id} not in first db")

    diff = []
    for i, (idx0, idx1) in enumerate(common):
        try:
            diff.append(data[0][idx0] - data[1][idx1])
        except Exception as e:
            logger.warning(f"error appeared {e}")

    fig, ax = plt.subplots()
    for d in diff:
        d.plot(ax)
        d.stats()

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="Plot measurements related fittings",
        epilog="Text at the bottom of help",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--db1", default="127.0.0.1", type=str, help="Mongo database url [default 127.0.0.1]")
    parser.add_argument("--port1", type=int, default=27017, help="Mongo port")
    parser.add_argument("--coll1", type=str, required=True, help="Mongo collection to plot")

    parser.add_argument("--db2", default="127.0.0.1", type=str, help="Mongo database url [default 127.0.0.1]")
    parser.add_argument("--port2", type=int, default=27017, help="Mongo port")
    parser.add_argument("--coll2", type=str, required=True, help="Mongo collection to plot")

    parser.add_argument("--sat", type=str, required=False, nargs="+", default=None, help="Satellite name")
    parser.add_argument("--site", type=str, required=False, nargs="+", default=None, help="Site name")
    parser.add_argument("--field", type=str, required=True, nargs="+")

    arg = parser.parse_args()
    plot_measurements(arg)
    # arg.func(arg)
