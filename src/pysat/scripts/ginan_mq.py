"""
This script fetches measurements data from two MongoDB collections and generates a plot of their differences.

The script provides a command-line interface that allows users to specify the databases and collections to use, as well
as the measurements and fields to plot. The script fetches the data from the specified databases, finds the common
measurements between the two collections, and generates a plot of the differences between the measurements.

The script consists of several functions that handle different aspects of the data processing, including connecting to
the databases, fetching the measurements, finding the common measurements, and plotting the differences. The script
uses the `pymongo` library to interact with the MongoDB databases and the `matplotlib` library to generate the plot.

Example usage:
    python ginan_mq.py --db1=mydb1 --coll1=mycoll1 --port1=27017 \
                               --db2=mydb2 --coll2=mycoll2 --port2=27017 \
                               --site=SITE1 SITE2 --sat=SAT1 SAT2 --field=field1 field2 \
                               --state=state1  --log-file=measurements.log
"""
import argparse
import logging
import sys
import threading
import queue
from typing import List, Optional

import matplotlib.pyplot as plt

from pysat.data.measurements import Measurements
from pysat.dbconnector import mongo
from pysat.utils.common import find_common
from pysat.utils.patterns import generate_list


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


def get_measurements(
    data_base: mongo.MongoDB,
    *,
    sat: Optional[str] = None,
    site: Optional[str] = None,
    state: Optional[str] = None,
    series: str = "",
    keys: Optional[dict] = None,
) -> List[Measurements]:
    """
    Retrieves measurements from a given MongoDB collection.

    :param data_base: An instance of MongoDB.
    :param sat: The name of the satellite for which to retrieve measurements. If None, all satellites are considered.
    :param site: The name of the site for which to retrieve measurements. If None, all sites are considered.
    :param state: The state of the measurement. If None, all states are considered.
    :param series: The series of the measurement. If None, all series are considered.
    :param keys: A dictionary of fields to include in the output document. If empty, all fields are included.

    :return: A list of Measurements objects.
    """
    if keys is None:
        raise ValueError("Keys Not defined")
    site_list = generate_list(site, data_base.mongo_content["Site"])
    sat_list = generate_list(sat, data_base.mongo_content["Sat"])
    collection = "Measurements" if state is None else "States"
    measurements_data = data_base.get_data(
        collection, sat=sat_list, site=site_list, state=state, series=series, keys=keys
    )

    measurements = []
    for data in measurements_data:
        try:
            measurements.append(Measurements(data))
            logger.debug(f"Found measurement {measurements[-1].id}")
        except ValueError:
            logger.warning(f"Measurement with ID {data['_id']} does not have values")
    return measurements


def log_diff_measurements(
    diff1: List[int], diff2: List[int], data1: List[Measurements], data2: List[Measurements]
) -> None:
    """
    Logs the differences between two measurements datasets.

    :param diff1: List of indices for measurements in data1 that were not found in data2.
    :param diff2: List of indices for measurements in data2 that were not found in data1.
    :param data1: List of Measurements objects from database 1.
    :param data2: List of Measurements objects from database 2.

    :return: None
    """
    for diff in diff1:
        logger.warning(f"Measurement with ID {data1[diff].id} not found in second database")
    for diff in diff2:
        logger.warning(f"Measurement with ID {data2[diff].id} not found in first database")


def make_diff(common, data1, data2):
    """
    Generate the diffrences between 2 list of Measurements objects

    :param common: List of tuples of indices of measurements that are common to both data1 and data2.
    :param data1: List of Measurements objects from the first data source.
    :param data2: List of Measurements objects from the second data source.
    :return: the list of the diffrences
    """
    diff = []
    for idx0, idx1 in common:
        try:
            diff.append(data1[idx0] - data2[idx1])
        except ValueError as value_error:
            logger.warning(f"Value error occurred: {value_error}")
    return diff


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


def write_stats(diff):
    """
    write statistics related to a list of measurements objects
    :param diff: list of Measruement objects
    :return:
    """
    [data.stats() for data in diff]


def get_measurements_thread(data_base, queue_store, **kwargs):
    """
    Gets measurement data from a MongoDB database and puts it into a queue.

    :param data_base: A MongoDB connection object.
    :param queue_store: A queue to store the fetched data.
    :param kwargs: Keyword arguments passed to the `get_measurements` function.

    :return: None
    """
    data = get_measurements(data_base, **kwargs)
    queue_store.put(data)


def connect_databases(args):
    """
    Connects to the MongoDB databases using the provided arguments.

    :param args: An argparse.Namespace object that contains the command-line arguments.
    :return: A tuple of dictionaries with the measurements objects.
    """
    keys = {k: k for k in args.field}
    queues = []
    threads = []
    data = []
    num_dbs = 2 if args.coll2 else 1
    for i in range(num_dbs):
        db_args = getattr(args, f"db{i+1}")
        coll_args = getattr(args, f"coll{i+1}")
        port_args = getattr(args, f"port{i+1}")
        db = mongo.MongoDB(url=db_args, data_base=coll_args, port=port_args)
        db.connect()
        db.get_content()
        queue_ = queue.Queue()
        queues.append(queue_)

        thread = threading.Thread(
            target=get_measurements_thread,
            args=(db, queue_),
            kwargs={"sat": args.sat, "site": args.site, "state": args.state, "series": "", "keys": keys},
        )
        threads.append(thread)
        thread.start()

    for i in range(num_dbs):
        threads[i].join()
        data.append(queues[i].get())

    return tuple(data)


def plot_measurements(args):
    """
    Fetches measurements data from two MongoDB collections and generates a plot of their differences.

    :param args: argparse.Namespace object that contains the command-line arguments.

    :return None
    """
    # create database connections
    data = connect_databases(args)
    if args.diff:
        if len(data) == 2:
            common, diff1, diff2 = find_common(data[0], data[1])
            log_diff_measurements(diff1, diff2, data[0], data[1])
            diff = make_diff(common, data[0], data[1])
        else:
            raise ValueError("Diff set up but don't have 2 datas")
    else:
        diff = []
        for single_data in data:
            diff.extend(single_data)
    write_stats(diff)
    if args.output is not False:
        plot_diff_measurements(diff, args.output)


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
        epilog="Text at the bottom of help",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--db1", default="127.0.0.1", type=str, help="Mongo database url [default 127.0.0.1]")
    parser.add_argument("--port1", type=int, default=27017, help="Mongo port")
    parser.add_argument("--coll1", type=str, required=True, help="Mongo collection to plot")

    parser.add_argument("--db2", default="127.0.0.1", type=str, help="Mongo database url [default 127.0.0.1]")
    parser.add_argument("--port2", type=int, default=27017, help="Mongo port")
    parser.add_argument("--coll2", type=str, required=False, help="Mongo collection to plot")

    parser.add_argument("--sat", type=str, required=False, nargs="+", default=None, help="Satellite name")
    parser.add_argument("--site", type=str, required=False, nargs="+", default=None, help="Site name")
    parser.add_argument("--field", type=str, required=True, nargs="+")
    parser.add_argument("--state", type=str, nargs=1, default=None)

    parser.add_argument("--diff", default=False, action="store_true")

    parser.add_argument("--output", nargs="?", const=True, default=False, help="output plot into a file or xdisplay")

    args = parser.parse_args()

    try:
        plot_measurements(args)
    except ValueError as error_value:
        logger.exception(f"Value error: {error_value}")
        sys.exit(1)
    except Exception as error:
        logger.exception(f"An error occurred: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
