import argparse
import os
import logging
import sys
from pathlib import Path
import json
from typing import Dict, List, Tuple

import numpy as np
from sklearn.model_selection import train_test_split

from sateda.io.sp3 import sp3, sp3_align
from sateda.core.transform.helmert import HelmertTransform
from sateda.data.satellite import Satellite, align_satellites


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)



def glob_files(paths):
    paths = map(Path,paths)
    return  [file_path for path in paths for file_path in path.parent.glob(path.name)]

    # return chain.from_iterable(path.parent.glob(path.name) for path in paths)


def parse_args() -> argparse.Namespace:
    """
    parse_args argument parser

    :return argparse.Namespace: parsed arguments
    """
    # print current directory
    print(os.getcwd())
    args = argparse.ArgumentParser("Helmert transformation")
    args.add_argument("--src", nargs='+', help="Source file(s)", type=str)
    args.add_argument("--target", nargs='+', help="Target file(s)", type=str)
    args.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    args.add_argument("-r", "--rotate", action="store_true", help="Rotate the data")
    args.add_argument("-o", "--output", help="Output file")
    args.add_argument("-m", "--mode", help="Mode of fitting, valid option per_sat, per_epoch, all", default="all")
    args.add_argument("-x", '--exclude', nargs='+', help="Exclude satellites", type=str)
    args.add_argument("-c", "--config", help="JSON config file")

    args = args.parse_args()
    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            config = json.load(f)
        for key in config:
            if hasattr(args, key):
                setattr(args, key, config[key])

    args.src = glob_files(args.src)
    args.target = glob_files(args.target)
    print(args.src)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return args


def run_helmert_transform():
    """
    Runs the Helmert transform based on the provided arguments.

    This function reads satellite data from source and target files, aligns the satellites,
    fits the transformation based on the specified mode, computes statistics, and logs the results.

    Args:
        None

    Returns:
        None
    """
    args = parse_args()
    data1 = sp3.read_multiple(files=args.src).as_satellites()
    data2 = sp3.read_multiple(files=args.target).as_satellites()
    satellite_names = list(set(data1.keys()).intersection(set(data2.keys())))
    print(args)
    if args.exclude:
        for sat in args.exclude:
            satellite_names.remove(sat)
       
    for _sat in satellite_names:
        align_satellites(data1[_sat], data2[_sat])
   
    if args.mode == "persat":
        helmert, transformed = fit_persat(data1, data2, satellite_names)
    elif args.mode == "perepoch":
        # raise ValueError("Not implemented yet")
        helmert, transformed = fit_perepoch(data1, data2, satellite_names)
    elif args.mode == "all":
        helmert, transformed = fit_all(data1, data2, satellite_names)
    else:
        raise ValueError("Invalid mode. Please choose 'persat', 'perepoch', or 'fit_all'.")
   
    stats = compute_stats(data1, data2, transformed, satellite_names)
   
    logger.info("       pre_x     pre_y     pre_z    pre_3d     post_x    post_y    post_z   post_3d")
    for d in sorted(satellite_names):
        data = stats[d]
        logger.info(
            f"{d}: "
            f"{data['pre_x']: .6f} {data['pre_y']: .6f} {data['pre_z']: .6f} {data['pre_3d']: .6f} "
            f"{data['post_x']: .6f} {data['post_y']: .6f} {data['post_z']: .6f} {data['post_3d']: .6f} "
        )
    logger.info(f" Estimated parameters:\n" f"   T: {helmert}")


def fit_perepoch(data1: dict, data2: dict, satellite_names: List[str]) -> (HelmertTransform, dict):
    """
    Fits a Helmert transformation model per epoch for the given satellite data.

    Args:
        data1 (dict): Dictionary containing satellite data for the first set of satellites.
        data2 (dict): Dictionary containing satellite data for the second set of satellites.
        satellite_names (list): List of satellite names.

    Returns:
        tuple: A tuple containing the fitted Helmert transformation model and the transformed satellite data.
    """
    transformed = {}

    times = np.unique(np.hstack([data1[satellite_name].time for satellite_name in satellite_names]))
    for satellite_name in satellite_names:
        transformed[satellite_name] = data1[satellite_name].copy()
        transformed[satellite_name].pos[:] = np.nan

    for time in times:
        data1_ = np.vstack(
            [
                data1[satellite_name].pos[data1[satellite_name].time == time] for satellite_name in satellite_names
            ]
        )
        data2_ = np.vstack(
            [
                data2[satellite_name].pos[data2[satellite_name].time == time] for satellite_name in satellite_names
            ]
        )
        data_train, data_test, target_train, target_test = train_test_split(data1_, data2_, test_size=0.20, random_state=42)
        loss = target_test - data_test
        logger.info(" on validation dataset ")
        logger.info("INIT  -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
        helmert = HelmertTransform()
        helmert.fit(data_train, target_train)
        loss = target_test - helmert.apply(data_test)
        logger.info("FINAL -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
        for satellite_name in satellite_names:
            if np.any(data1[satellite_name].time == time):
                idx = np.where(data1[satellite_name].time == time)[0]
                transformed[satellite_name].pos[idx] = helmert.apply(data1[satellite_name].pos[idx])

    return helmert, transformed

def fit_persat(data1: Dict[str, Satellite], data2: Dict[str, Satellite], satellite_names: List[str]) -> Tuple[HelmertTransform, Dict[str, Satellite]]:
    """
    Fits a Helmert transformation model to align satellite positions.

    Args:
        data1 (Dict[str, Satellite]): Dictionary of satellite data for the first dataset.
        data2 (Dict[str, Satellite]): Dictionary of satellite data for the second dataset.
        satellite_names (List[str]): List of satellite names to be processed.

    Returns:
        Tuple[HelmertTransform, Dict[str, Satellite]]: A tuple containing the fitted Helmert transformation model and the transformed satellite data.
    """
    transformed = {}
    for satellite_name in satellite_names:
        data1_ = data1[satellite_name].pos
        data2_ = data2[satellite_name].pos
        transformed[satellite_name] = Satellite(sat=satellite_name)
        data_train, data_test, target_train, target_test = train_test_split(data1_, data2_, test_size=0.20, random_state=42)
        loss = target_test - data_test
        logger.info(" on validation dataset ")
        logger.info("INIT  -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
        helmert = HelmertTransform()
        helmert.fit(data_train, target_train)
        loss = target_test - helmert.apply(data_test)
        logger.info("FINAL -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
        transformed[satellite_name].time = data1[satellite_name].time
        transformed[satellite_name].pos = helmert.apply(data1[satellite_name].pos)
    return helmert, transformed
 
def fit_all(data1, data2, satellite_names):
    data1_ = np.vstack(
        [
            data1[satellite_name].pos for satellite_name in satellite_names
        ]
    )
    data2_ = np.vstack(
        [
           data2[satellite_name].pos for satellite_name in satellite_names
        ]
    )
  
    data_train, data_test, target_train, target_test = train_test_split(data1_, data2_, test_size=0.20, random_state=42)
  
    loss = target_test - data_test
    logger.info(" on validation dataset ")
    logger.info("INIT  -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
    helmert = HelmertTransform()
    helmert.fit(data_train, target_train)
    loss = target_test - helmert.apply(data_test)
    logger.info("FINAL -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))

    transformed = {}
    for satellite_name in satellite_names:
        transformed[satellite_name] = Satellite(sat=satellite_name)
        transformed[satellite_name].time = data1[satellite_name].time
        transformed[satellite_name].pos = helmert.apply(data1[satellite_name].pos)

    return helmert, transformed


def compute_stats(source, target, transformed, satellite_names):
    stats = {}
    for satellite_name in satellite_names:
        loss = source[satellite_name].pos - target[satellite_name].pos
        stats[satellite_name] = {}
        stats[satellite_name]["pre_x"] = np.sqrt(np.mean(loss[:, 0] ** 2))
        stats[satellite_name]["pre_y"] = np.sqrt(np.mean(loss[:, 1] ** 2))
        stats[satellite_name]["pre_z"] = np.sqrt(np.mean(loss[:, 2] ** 2))
        stats[satellite_name]["pre_3d"] = np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2))
        loss = transformed[satellite_name].pos - target[satellite_name].pos
        stats[satellite_name]["post_x"] = np.sqrt(np.mean(loss[:, 0] ** 2))
        stats[satellite_name]["post_y"] = np.sqrt(np.mean(loss[:, 1] ** 2))
        stats[satellite_name]["post_z"] = np.sqrt(np.mean(loss[:, 2] ** 2))
        stats[satellite_name]["post_3d"] = np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2))
    return stats


if __name__ == "__main__":
    run_helmert_transform()