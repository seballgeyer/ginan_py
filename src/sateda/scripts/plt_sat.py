"""
script to plot satellite residual
More infos to add at a later stage
"""
import argparse
import logging
import sys

import matplotlib.pyplot as plt
import numpy as np

from sateda.data.satellite import satellite
from sateda.dbconnector import mongo


class CustomFormatter(logging.Formatter):
    """
    reformating logging class
    @todo move to the possible __init__.py
    """
    def format(self, record):
        if record.levelno == logging.INFO:
            return record.getMessage()
        return f"{record.levelname} > {record.getMessage()}"


logger = logging.getLogger("main")
formatter = CustomFormatter()
logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


def read(arg):
    """
    function to read the data from mongo
    """
    database = mongo.MongoDB(url=arg.db, data_base=arg.coll, port=27018)
    database.connect()
    print(database)
    sat = satellite(database, sat=arg.sat)
    sat.get_postfit()
    sat.get_state()
    rms = sat.get_rms()
    logger.info(
        f"{arg.coll} {arg.sat}   {np.array2string(rms[:3], precision=6, floatmode='fixed')}   "
    )
    if arg.to_rac:
        rms_rac = sat.get_rac()
        logger.info(f"{np.array2string(rms_rac[:3], precision=6, floatmode='fixed')}")
    logger.info(f"=> {rms[3]:.6f}")
    sat.get_state()
    return sat


def plot(arg, sat):
    """
    function to plot the data
    """
    _, axes = plt.subplots(nrows=3)
    if arg.to_rac:
        residuals = sat.rac.transpose()
        y_label = ["r", "a", "c"]
    else:
        residuals = sat.residual.transpose()
        y_label = ["x", "y", "z"]

    for axis, data in zip(axes, residuals):
        axis.plot(sat.time, data)
    for axis, label in zip(axes, y_label):
        axis.set_ylabel(label)
    plt.savefig(f"plt_{arg.coll}_{arg.sat}.pdf", bbox_inches="tight")


def main_residuals(arg):
    orbit = read(arg)
    plot(arg, orbit)


def main_states(arg):
    print("not implemented yet")


if __name__ == "__main__":
    plt.style.use(["seaborn-v0_8-ticks"])
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="Plot satellite related fittings",
        epilog="Text at the bottom of help",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--db",
        default="127.0.0.1",
        type=str,
        help="Mongo database url [default 127.0.0.1]",
    )
    parser.add_argument("--coll", type=str, required=True, help="Mongo collection to plot")
    parser.add_argument("-s", "--sat", type=str, required=True, help="Satellite name")

    subparser = parser.add_subparsers(help="sub-command help")

    parser_residual_option = subparser.add_parser("res", help="plotting residual")
    parser_residual_option.add_argument("--to_rac", action="store_true", default=False, help="plot in R, A, C")
    parser_residual_option.set_defaults(func=main_residuals)

    parser_state_option = subparser.add_parser("state", help="plotting states")
    parser_state_option.add_argument("state", help="which state to plot?", type=str, nargs="+")
    parser_state_option.set_defaults(func=main_states)

    args = parser.parse_args()
    print(args)
    args.func(args)
