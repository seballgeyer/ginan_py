import argparse
import os
import logging
import sys

import json
import numpy as np
from sklearn.model_selection import train_test_split

from sateda.io.sp3 import sp3, sp3_align
from sateda.core.transform.helmert import HelmertTransform


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)


def parse_args():
    # print current directory
    print(os.getcwd())
    args = argparse.ArgumentParser("Helmert transformation")
    args.add_argument("input1", help="Input file")
    args.add_argument("input2", help="Input file2")
    args.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    args.add_argument("-r", "--rotate", action="store_true", help="Rotate the data")
    args.add_argument("-o", "--output", help="Output file")
    args.add_argument("-c", "--config", help="JSON config file")

    args = args.parse_args()
    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
        if "verbose" in config:
            args.verbose = config["verbose"]
        if "rotate" in config:
            args.rotate = config["rotate"]
        if "output" in config:
            args.output = config["output"]
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return args


def main():
    args = parse_args()
    data1 = sp3.read(file_or_string=args.input1)
    data2 = sp3.read(file_or_string=args.input2)

    data1, data2 = sp3_align(data1, data2)
    time = np.hstack([data1.data[satellite_name]["time"] for satellite_name in data1.data.keys()])

    satellite_names = list(set(data1.data.keys()).intersection(set(data2.data.keys())))
    stats = {}
    for satellite_name in satellite_names:
        data1_ = np.vstack(
            [data1.data[satellite_name]["x"], data1.data[satellite_name]["y"], data1.data[satellite_name]["z"]]
        ).transpose()

        data2_ = np.vstack(
            [data2.data[satellite_name]["x"], data2.data[satellite_name]["y"], data2.data[satellite_name]["z"]]
        ).transpose()

        loss = data1_ - data2_
        stats[satellite_name] = {}
        stats[satellite_name]["pre_x"] = np.sqrt(np.mean(loss[:, 0] ** 2))
        stats[satellite_name]["pre_y"] = np.sqrt(np.mean(loss[:, 1] ** 2))
        stats[satellite_name]["pre_z"] = np.sqrt(np.mean(loss[:, 2] ** 2))
        stats[satellite_name]["pre_3d"] = np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2))

    data1_ = np.hstack(
        [
            np.vstack(
                [data1.data[satellite_name]["x"], data1.data[satellite_name]["y"], data1.data[satellite_name]["z"]]
            )
            for satellite_name in satellite_names
        ]
    ).transpose()
    data2_ = np.hstack(
        [
            np.vstack(
                [data2.data[satellite_name]["x"], data2.data[satellite_name]["y"], data2.data[satellite_name]["z"]]
            )
            for satellite_name in satellite_names
        ]
    ).transpose()

    data_train, data_test, target_train, target_test = train_test_split(data1_, data2_, test_size=0.2, random_state=42)

    # split data1 and data2 in a train and test set (80, 20%), same index for both
    loss = target_test - data_test
    logger.info(" on validation dataset ")
    logger.info("INIT  -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))

    helmert = HelmertTransform()
    helmert.fit(data_train, target_train)

    loss = target_test - helmert.apply(data_test)
    logger.info("FINAL -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(nrows=3, ncols=2, figsize=(10,10))
    
    for satellite_name in satellite_names:
        data1_ = np.vstack(
            [data1.data[satellite_name]["x"], data1.data[satellite_name]["y"], data1.data[satellite_name]["z"]]
        ).transpose()

        data2_ = np.vstack(
            [data2.data[satellite_name]["x"], data2.data[satellite_name]["y"], data2.data[satellite_name]["z"]]
        ).transpose()

        loss = helmert.apply(data1_) - data2_
        for i in range(3):
            ax[i, 1].plot( loss[:, i], label=satellite_name)
            ax[i, 0].plot( (data1_-data2_)[:, i], label=satellite_name)
        stats[satellite_name]["post_x"] = np.sqrt(np.mean(loss[:, 0] ** 2))
        stats[satellite_name]["post_y"] = np.sqrt(np.mean(loss[:, 1] ** 2))
        stats[satellite_name]["post_z"] = np.sqrt(np.mean(loss[:, 2] ** 2))
        stats[satellite_name]["post_3d"] = np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2))
    plt.savefig("helmert.png")
    satellite_names.sort()
    logger.info("       pre_x     pre_y     pre_z    pre_3d     post_x    post_y    post_z   post_3d")
    for d in satellite_names:
        data = stats[d]
        logger.info(
            f"{d}: "
            f"{data['pre_x']: .6f} {data['pre_y']: .6f} {data['pre_z']: .6f} {data['pre_3d']: .6f} "
            f"{data['post_x']: .6f} {data['post_y']: .6f} {data['post_z']: .6f} {data['post_3d']: .6f} "
        )
    logger.info(f" Estimated parameters:\n" f"   T: {helmert}")


if __name__ == "__main__":
    main()
