import logging
import argparse
import sys


import matplotlib.pyplot as plt
import numpy as np

from pysat.data.measurements import measurements
from pysat.dbconnector import mongo
from pysat.utils.patterns import match_patterns


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


def plot_states(args):
    db = mongo.MongoDB(url=args.db, data_base=args.coll)
    if args.site:
        sites = [value for value in db.mongo_content["Site"] if match_patterns(args.site, value)]
    else:
        sites = [""]

    if args.sat:
        sats = [value for value in db.mongo_content["Sat"] if match_patterns(args.sat, value)]
    else:
        sats = [""]

    keys = {k: k for k in args.field}
    dd = db.get_data("States", sat=sats, site=sites, state=args.state, series="", keys=keys)
    data = []

    data = []
    for d in dd:
        try:
            data.append(measurements(d))
            logger.info(f"Find {data[-1].id}")
        except ValueError as e:
            logger.warning(d["_id"], "doesn't have values")

    for d in data:
        d.demean()

    fig, ax = plt.subplots()
    for d in data:
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
    parser.add_argument("--db", default="127.0.0.1", type=str, help="Mongo database url [default 127.0.0.1]")
    parser.add_argument("--coll", type=str, required=True, help="Mongo collection to plot")
    parser.add_argument("--sat", type=str, required=False, nargs="+", default=None, help="Satellite name")
    parser.add_argument("--site", type=str, required=False, nargs="+", help="Site name")
    parser.add_argument("--state", type=str, required=True, help="State name")
    parser.add_argument("--field", type=str, required=True, nargs="+")

    arg = parser.parse_args()
    plot_states(arg)
    # arg.func(arg)
