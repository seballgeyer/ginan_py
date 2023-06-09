"""
This script fetches measurements data from two MongoDB collections and generates a plot of their differences.

The script provides a command-line interface that allows users to specify the databases and collections to use, as well
as the measurements and fields to plot. The script fetches the data from the specified databases, finds the common
measurements between the two collections, and generates a plot of the differences between the measurements.

The script consists of several functions that handle different aspects of the data processing, including connecting to
the databases, fetching the measurements, finding the common measurements, and plotting the differences. The script
uses the `pymongo` library to interact with the MongoDB databases and the `matplotlib` library to generate the plot.

Example usage:
    python ginan_mq.py --db1=mydb1 --dbname1=mycoll1 --port1=27017 \
                               --db2=mydb2 --dbname2=mycoll2 --port2=27017 \
                               --site=SITE1 SITE2 --sat=SAT1 SAT2 --field=field1 field2 \
                               --state=state1  --log-file=measurements.log
"""
import argparse
import logging
import queue
import sys
import threading
from typing import List, Optional

import matplotlib.pyplot as plt

import sateda
from sateda.data.measurements import Measurements
from sateda.data.clocks import Clocks
from sateda.dbconnector.mongo import MongoDB
from sateda.utils.common import find_common
from sateda.utils.patterns import generate_list


class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter that overrides the default formatter's format method
    to only display the log message for INFO logs and display the log level and message
    for other logs.

    Args:
        None

    Returns:
        None
    """

    def format(self, record):
        if record.levelno == logging.INFO:
            return record.getMessage()
        return f"{record.levelname} > {record.getMessage()}"


logger = logging.getLogger("main")
formatter = CustomFormatter()
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)




def plot_diff_measurements(diff, output_type):
    """
    Plots the differences between two sets of measurements.

    :param diff: List of Measurements differences objects.

    :return: None
    """

    _fig, axis = plt.subplots()
    for data in diff:
        data.plot(axis)
    if output_type is True:
        plt.show()
    else:
        plt.savefig(output_type, bbox_inches="tight")




def connect_databases(args):
    """
    Connects to the MongoDB databases using the provided arguments.

    :param args: An argparse.Namespace object that contains the command-line arguments.
    :return: A tuple of dictionaries with the measurements objects.
    """
    print(args)
    print(args['db1'])
    with MongoDB(args["db1"], data_base=args["dbname1"], port=args["port1"]) as client:
        try:
            sat_list = generate_list(args["sat"], client.mongo_content["Sat"])
            print(sat_list)
            if args["exclude"]:
                sat_exlude = generate_list(args["exclude"], client.mongo_content["Sat"])
                #remove the value from sat_exclude from the sat_list values
                print("exclude", sat_exlude)
                sat_list = [sat for sat in sat_list if sat not in sat_exlude]
            print(sat_list)
            data = client.get_data_to_measurement(
                "States",
                ["SAT_CLOCK"],
                [""],
                sat_list,
                [args["coll1"], args["coll2"]],
                ["x"],
            )
        except Exception as err:
            print(str(err))
    clocks = Clocks(data, satlist=sat_list, series=args["coll1"], series_base=args["coll2"])
    clocks.process()
    
    fig, axis = plt.subplots()
    for data in clocks.process():
        axis.plot(data.epoch, data.data["x"], label=data.id)
    # axis.legend()
    plt.show()
        
    # keys = {k: k for k in args["field"]}
    # queues = []
    # threads = []
    # data = []
    # num_dbs = 2 if args["dbname2"] else 1
    # for i in range(num_dbs):
    #     db_args = args[f"db{i+1}"]
    #     coll_args = args[f"dbname{i+1}"]
    #     port_args = args[f"port{i+1}"]
    #     mongo_db = mongo.MongoDB(url=db_args, data_base=coll_args, port=port_args)
    #     mongo_db.connect()
    #     mongo_db.get_content()
    #     queue_ = queue.Queue()
    #     queues.append(queue_)

    #     thread = threading.Thread(
    #         target=get_measurements_thread,
    #         args=(mongo_db, queue_),
    #         kwargs={
    #             "sat": args["sat"],
    #             "site": args["site"],
    #             "state": args["state"],
    #             "series": "",
    #             "keys": keys,
    #         },
    #     )
    #     threads.append(thread)
    #     thread.start()

    # for i in range(num_dbs):
    #     threads[i].join()
    #     data.append(queues[i].get())

    # return tuple(data)


def plot_measurements(args):
    """
    Fetches measurements data from two MongoDB collections and generates a plot of their differences.

    :param args: argparse.Namespace object that contains the command-line arguments.

    :return None
    """
    # create database connections
    data = connect_databases(args)
    # if args["diff"]:
    #     if len(data) == 2:
    #         common, diff1, diff2 = find_common(data[0], data[1])
    #         log_diff_measurements(diff1, diff2, data[0], data[1])
    #         diff = make_diff(common, data[0], data[1])
    #     else:
    #         raise ValueError("Diff set up but don't have 2 datas")
    # else:
    #     diff = []
    #     for single_data in data:
    #         print(single_data)
    #         diff.extend(single_data)
    # write_stats(diff)
    # if args["output"] is not False:
    #     plot_diff_measurements(diff, args["output"])


def main():
    """
    Entry point for the script. Parses command line arguments and calls the appropriate function based on the user's
    input.

    The script takes two MongoDB collections as input and generates a plot of the measurements related fittings between
    them.
    The user can specify the databases and collections to connect to, as well as the satellites, sites, and fields to
    plot.

    Usage: python ginan_mq.py [--db1 <database_url>] [--port1 <port_number>]
                                    [--db2 <database_url>] [--port2 <port_number>]
                                     --coll1 <collection_name> --coll2 <collection_name>
                                     --site <site_name> --sat <satellite_name>
                                     --field <field_name> [<field_name> ...]
                                    [--state <state_name>]

    :param None
    :return None
    """
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="Plot measurements related fittings",
        epilog=f"(c) Sebastien Allgeyer {sateda.__version__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--db1",
        default="127.0.0.1",
        type=str,
        help="Mongo database url [default 127.0.0.1]",
    )
    parser.add_argument("--port1", type=int, default=27017, help="Mongo port")
    parser.add_argument("--dbname1", type=str, required=True, help="Mongo collection to plot")
    parser.add_argument("--coll1", type=str, required=True, help="Mongo collection to plot")
    parser.add_argument("--coll2", type=str, required=True, help="Mongo collection to plot")

    parser.add_argument(
        "--sat",
        type=str,
        required=False,
        nargs="+",
        default=None,
        help="Satellite name",
    )
    
    parser.add_argument(
        "--exclude",
        type=str,
        required=False,
        nargs="+",
        default=None,
        help="Satellite name",
    )

    parser.add_argument(
        "--output",
        nargs="?",
        const=True,
        default=False,
        help="output plot into a file or xdisplay",
    )

    args = parser.parse_args()

    try:
        plot_measurements(vars(args))
    except ValueError as error_value:
        logger.exception(f"Value error: {error_value}")
        sys.exit(1)
    # except Exception as error:
    #     logger.exception(f"An error occurred: {error}")
    #     sys.exit(1)


if __name__ == "__main__":
    main()
