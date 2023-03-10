import argparse

import matplotlib.pyplot as plt
import numpy as np

from pysat.data.measurements import measurements
from pysat.dbconnector import mongo
from pysat.utils.patterns import match_patterns


def plot_measurements(args):
    db = mongo.MongoDB(url=args.db, data_base=args.coll)
    print(arg.site)
    print(db.mongo_content["Site"])
    print(db.mongo_content["Sat"])

    sites = [value for value in db.mongo_content["Site"] if match_patterns(args.site, value)]

    sats = [value for value in db.mongo_content["Sat"] if match_patterns(args.sat, value)]
    # sites = match_patterns(args.site, db.mongo_content["Site"])
    print(sites, sats)
    print(args)
    # check
    print(db.mongo_content)
    # if args.sat not in db.mongo_content["Sat"]:
    # raise "error"
    dd = db.get_data("Measurements", sat=sats, site=sites, state=None, series="", keys={args.field[0]: args.field[0]})
    data = []
    print(len(dd))
    # for d in dd:
    #     for k in d:
    #         print(k)
    # print(args)

    data = []
    for d in dd:
        try:
            data.append(measurements(d))
        except ValueError as e:
            print(d["_id"], "doesn't have values")

    for d in data:
        print("*", d.id)

    fig, ax = plt.subplots()
    for d in data:
        d.plot(ax)
        d.stats()

    plt.show()


if __name__ == "__main__":
    plt.style.use(["seaborn-v0_8-ticks"])
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="Plot measurements related fittings",
        epilog="Text at the bottom of help",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--db", default="127.0.0.1", type=str, help="Mongo database url [default 127.0.0.1]")
    parser.add_argument("--coll", type=str, required=True, help="Mongo collection to plot")
    parser.add_argument("--sat", type=str, required=True, nargs="+", help="Satellite name")
    parser.add_argument("--site", type=str, required=True, nargs="+", help="Site name")
    parser.add_argument("--field", type=str, required=True, nargs="+")

    arg = parser.parse_args()
    plot_measurements(arg)
    # arg.func(arg)
