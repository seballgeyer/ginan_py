import argparse
import logging
import sys

import matplotlib.pyplot as plt

from sateda.data.measurements import Measurements
from sateda.dbconnector import mongo
from sateda.utils.patterns import generate_list


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
    db = mongo.MongoDB(url=args["db"], data_base=args["coll"], port=args["port"])
    logger.info(arg.site)
    # print(db.mongo_content["Site"])
    # print(db.mongo_content["Sat"])

    sites = generate_list(args["site"], db.mongo_content["Site"])
    sats = generate_list(args["sat"], db.mongo_content["Sat"])
    # sites = match_patterns(args.site, db.mongo_content["Site"])
    # print(sites, sats)
    # print(args)
    # # check
    # print(db.mongo_content)
    # if args.sat not in db.mongo_content["Sat"]:
    # raise "error"
    keys = {k: k for k in args["field"]}
    dd = db.get_data("Measurements", sat=sats, site=sites, state=None, series="", keys=keys)
    data = []
    # print(len(dd))
    # for d in dd:
    #     for k in d:
    #         print(k)
    # print(args)

    data = []
    for d in dd:
        try:
            data.append(Measurements(d))
        except ValueError as e:
            logger.warning(f"{d['_id']} doesn't have values")

    for d in data:
        print("*", d.id)

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
    parser.add_argument(
        "--db",
        default="127.0.0.1",
        type=str,
        help="Mongo database url [default 127.0.0.1]",
    )
    parser.add_argument("--port", type=int, default=27017, help="Mongo port")
    parser.add_argument("--coll", type=str, required=True, help="Mongo collection to plot")
    parser.add_argument("--sat", type=str, required=True, nargs="+", help="Satellite name")
    parser.add_argument("--site", type=str, required=True, nargs="+", help="Site name")
    parser.add_argument("--field", type=str, required=True, nargs="+")

    arg = parser.parse_args()
    plot_measurements(arg)
    # arg.func(arg)
