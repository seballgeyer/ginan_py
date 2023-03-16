"""
This script fetches measurements data from two MongoDB collections and generates a plot of their differences.

The script provides a command-line interface that allows users to specify the databases and collections to use, as well
as the measurements and fields to plot. The script fetches the data from the specified databases, finds the common
measurements between the two collections, and generates a plot of the differences between the measurements.

The script consists of several functions that handle different aspects of the data processing, including connecting to
the databases, fetching the measurements, finding the common measurements, and plotting the differences. The script
uses the `pymongo` library to interact with the MongoDB databases and the `matplotlib` library to generate the plot.

Example usage:
    python measurements.py --db1=mydb1 --coll1=mycoll1 --port1=27017 \
                           --db2=mydb2 --coll2=mycoll2 --port2=27017 \
                           --site=SITE1 SITE2 --sat=SAT1 SAT2 --field=field1 field2 \
                           --measurement=meas1 meas2 --log-file=measurements.log
"""
import argparse
import logging
import sys
from typing import Union, List

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
logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


def get_measurements(
    db: mongo.MongoDB,
    sat: Union[str, None] = None,
    site: Union[str, None] = None,
    state: Union[str, None] = None,
    series: str = "",
    keys: Union[dict, None] = None,
) -> List[Measurements]:
    """
    Retrieves measurements from a given MongoDB collection.

    :param db: An instance of MongoDB.
    :param sat: The name of the satellite for which to retrieve measurements. If None, all satellites are considered.
    :param site: The name of the site for which to retrieve measurements. If None, all sites are considered.
    :param state: The state of the measurement. If None, all states are considered.
    :param series: The series of the measurement. If None, all series are considered.
    :param keys: A dictionary of fields to include in the output document. If empty, all fields are included.

    :return: A list of Measurements objects.
    """
    if keys is None:
        raise ValueError("Keys Not defined")
    sites = generate_list(site, db.mongo_content["Site"])
    sats = generate_list(sat, db.mongo_content["Sat"])
    measurements_data = db.get_data("Measurements", sat=sats, site=sites, state=state, series=series, keys=keys)

    measurements = []
    for data in measurements_data:
        try:
            measurements.append(Measurements(data))
            logger.info(f"Found measurement {measurements[-1].measurement_id}")
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
    for d in diff1:
        logger.warning(f"Measurement with ID {data1[d].id} not found in second database")
    for d in diff2:
        logger.warning(f"Measurement with ID {data2[d].id} not found in first database")


def plot_diff_measurements(common, data1, data2):
    """
    Plots the differences between two sets of measurements.

    :param common: List of tuples of indices of measurements that are common to both data1 and data2.
    :param data1: List of Measurements objects from the first data source.
    :param data2: List of Measurements objects from the second data source.

    :return: None
    """
    diff = []
    for idx0, idx1 in common:
        try:
            diff.append(data1[idx0] - data2[idx1])
        except Exception as e:
            logger.warning(f"Error occurred: {e}")

    fig, ax = plt.subplots()
    for d in diff:
        d.plot(ax)
        d.stats()

    plt.show()


def plot_measurements(args):
    """
    Fetches measurements data from two MongoDB collections and generates a plot of their differences.

    :param args: argparse.Namespace object that contains the command-line arguments.

    :return None
    """
    keys = {k: k for k in args.field}
    with mongo.MongoDB(url=args.db1, data_base=args.coll1, port=args.port1) as db1:
        data1 = get_measurements(db1, args.sat, args.site, None, "", keys)

    with mongo.MongoDB(url=args.db2, data_base=args.coll2, port=args.port2) as db2:
        data2 = get_measurements(db2, args.sat, args.site, None, "", keys)

    common, diff1, diff2 = find_common(data1, data2)
    log_diff_measurements(diff1, diff2, data1, data2)
    plot_diff_measurements(common, data1, data2)


def main():
    """
    Entry point for the script. Parses command line arguments and calls the appropriate function based on the user's
    input.

    The script takes two MongoDB collections as input and generates a plot of the measurements related fittings between
    them.
    The user can specify the databases and collections to connect to, as well as the satellites, sites, and fields to
    plot.

    Usage: python script.py [--db1 <database_url>] [--db2 <database_url>] [--port1 <port_number>]
                            [--port2 <port_number>]
                             --coll1 <collection_name> --coll2 <collection_name>
                             --site <site_name> --sat <satellite_name>
                             --field <field_name> [<field_name> ...]

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
    parser.add_argument("--coll2", type=str, required=True, help="Mongo collection to plot")

    parser.add_argument("--sat", type=str, required=False, nargs="+", default=None, help="Satellite name")
    parser.add_argument("--site", type=str, required=False, nargs="+", default=None, help="Site name")
    parser.add_argument("--field", type=str, required=True, nargs="+")

    args = parser.parse_args()

    try:
        plot_measurements(args)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
