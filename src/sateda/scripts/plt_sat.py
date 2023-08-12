import argparse
import logging
import sys

import matplotlib.pyplot as plt
import numpy as np

from sateda.data.satellite import satellite
from sateda.dbconnector import mongo


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


def read(args):
    print(args)
    db = mongo.MongoDB(url=args.db, data_base=args.coll, port=27018)
    db.connect()
    print(db.get_list_db())
    sat = satellite(db, sat=args.sat)
    sat.get_postfit()
    # sat.get_state()
    rms = sat.get_rms()
    logger.info(
        f"{args.coll} {arg.sat}   {np.array2string(rms[:3], precision=6, floatmode='fixed')}   "
    )
    if args.to_rac:
        rms_rac = sat.get_rac()
        logger.info(f"{np.array2string(rms_rac[:3], precision=6, floatmode='fixed')}")
    logger.info(f"=> {rms[3]:.6f}")
    sat.get_state()
    return sat


def plot(args, sat):
    fig, ax = plt.subplots(nrows=3)
    if args.to_rac:
        r = sat.rac.transpose()
        y_label = ["r", "a", "c"]
    else:
        r = sat.residual.transpose()
        y_label = ["x", "y", "z"]

    for a, d in zip(ax, r):
        a.plot(sat.time, d)
    for a, l in zip(ax, y_label):
        a.set_ylabel(l)
    for d in r:
        print(np.sqrt(np.mean(np.square(d))))
    res3d2 = np.square(r).sum(axis=0)
    print("3d RMS", np.sqrt(np.mean(res3d2)))
    plt.savefig(f"plt_{args.coll}_{args.sat}.pdf", bbox_inches="tight")


def main_residuals(arg):
    orbit = read(arg)
    plot(arg, orbit)


def main_states(arg):
    print(arg)
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

    arg = parser.parse_args()
    arg.func(arg)
