import argparse
import os
import logging
import sys
from pathlib import Path
import json
from itertools import chain

import numpy as np
from sklearn.model_selection import train_test_split

from sateda.io.sp3 import sp3, sp3_align
from sateda.core.transform.helmert import HelmertTransform
from sateda.data.satellite import Satellite, align_satellites
import argparse
import os
import logging
import sys
from pathlib import Path
import json
from itertools import chain
import numpy as np
from sklearn.model_selection import train_test_split
from sateda.io.sp3 import sp3, sp3_align
from sateda.core.transform.helmert import HelmertTransform
from sateda.data.satellite import Satellite, align_satellites
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)



def glob_files(paths):
    paths = map(Path,paths)
    return  [file_path for path in paths for file_path in path.parent.glob(path.name)]

    # return chain.from_iterable(path.parent.glob(path.name) for path in paths)


def parse_args():
    # print current directory
    print(os.getcwd())
    args = argparse.ArgumentParser("Helmert transformation")
    args.add_argument("--src", nargs='+', help="Source file(s)", type=str)
    args.add_argument("--target", nargs='+', help="Target file(s)", type=str)
    args.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    args.add_argument("-r", "--rotate", action="store_true", help="Rotate the data")
    args.add_argument("-o", "--output", help="Output file")
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


def main():
    args = parse_args()
    data1 = sp3.read_multiple(files=args.src).as_satellites()
    data2 = sp3.read_multiple(files=args.target).as_satellites()
    satellite_names = list(set(data1.keys()).intersection(set(data2.keys())))
    satellite_names.remove('G15')
    # satellite_names=['G01']
    for _sat in satellite_names:
        align_satellites(data1[_sat], data2[_sat])
    helmert, stats = fit_persat(data1, data2, satellite_names)
    # helmert, stats = fit_perepoch(data1, data2, satellite_names)
    logger.info("       pre_x     pre_y     pre_z    pre_3d     post_x    post_y    post_z   post_3d")
    for d in sorted(satellite_names):
        data = stats[d]
        logger.info(
            f"{d}: "
            f"{data['pre_x']: .6f} {data['pre_y']: .6f} {data['pre_z']: .6f} {data['pre_3d']: .6f} "
            f"{data['post_x']: .6f} {data['post_y']: .6f} {data['post_z']: .6f} {data['post_3d']: .6f} "
        )
    logger.info(f" Estimated parameters:\n" f"   T: {helmert}")
    
    
def fit_perepoch(data1, data2, satellite_names):
    stats = {}
    for satellite_name in satellite_names:
        data1_ = data1[satellite_name].pos
        data2_ = data2[satellite_name].pos
        loss = data1_ - data2_
        stats[satellite_name] = {}
        stats[satellite_name]["pre_x"] = np.sqrt(np.mean(loss[:, 0] ** 2))
        stats[satellite_name]["pre_y"] = np.sqrt(np.mean(loss[:, 1] ** 2))
        stats[satellite_name]["pre_z"] = np.sqrt(np.mean(loss[:, 2] ** 2))
        stats[satellite_name]["pre_3d"] = np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2))
        stats[satellite_name]["res_x"] = 0
        stats[satellite_name]["res_y"] = 0
        stats[satellite_name]["res_z"] = 0
        stats[satellite_name]["res_3d"] = 0
        stats[satellite_name]["nres"] = 0
        
    times = np.unique(np.hstack([data1[satellite_name].time for satellite_name in satellite_names]))
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
                data1_ = helmert.apply(data1[satellite_name].pos[data1[satellite_name].time == time] )
                data2_ = data2[satellite_name].pos[data2[satellite_name].time == time] 
                loss = data1_ - data2_
                stats[satellite_name]["res_x"] += loss[0, 0] ** 2
                stats[satellite_name]["res_y"] += loss[0, 1] ** 2
                stats[satellite_name]["res_z"] += loss[0, 2] ** 2
                stats[satellite_name]["res_3d"] += np.linalg.norm(loss) ** 2
                stats[satellite_name]["nres"] += 1

    for satellite_name in satellite_names:
        stats[satellite_name]["post_x"] = np.sqrt(stats[satellite_name]["res_x"] / stats[satellite_name]["nres"])
        stats[satellite_name]["post_y"] = np.sqrt(stats[satellite_name]["res_y"] / stats[satellite_name]["nres"])
        stats[satellite_name]["post_z"] = np.sqrt(stats[satellite_name]["res_z"] / stats[satellite_name]["nres"])
        stats[satellite_name]["post_3d"] = np.sqrt(stats[satellite_name]["res_3d"] / stats[satellite_name]["nres"])
    return helmert, stats

def fit_persat(data1, data2, satellite_names):
    stats = {}
    for satellite_name in satellite_names:
        data1_ = data1[satellite_name].pos
        data2_ = data2[satellite_name].pos
        loss = data1_ - data2_
        stats[satellite_name] = {}
        stats[satellite_name]["pre_x"] = np.sqrt(np.mean(loss[:, 0] ** 2))
        stats[satellite_name]["pre_y"] = np.sqrt(np.mean(loss[:, 1] ** 2))
        stats[satellite_name]["pre_z"] = np.sqrt(np.mean(loss[:, 2] ** 2))
        stats[satellite_name]["pre_3d"] = np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2))
        data_train, data_test, target_train, target_test = train_test_split(data1_, data2_, test_size=0.20, random_state=42)
        loss = target_test - data_test
        logger.info(" on validation dataset ")
        logger.info("INIT  -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
        helmert = HelmertTransform()
        helmert.fit(data_train, target_train)
        loss = target_test - helmert.apply(data_test)
        logger.info("FINAL -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
        loss = helmert.apply(data1_) - data2_
        stats[satellite_name]["post_x"] = np.sqrt(np.mean(loss[:, 0] ** 2))
        stats[satellite_name]["post_y"] = np.sqrt(np.mean(loss[:, 1] ** 2))
        stats[satellite_name]["post_z"] = np.sqrt(np.mean(loss[:, 2] ** 2))
        stats[satellite_name]["post_3d"] = np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2))
    return helmert, stats
    
    
def fit_all(data1, data2, satellite_names):
    stats = {}
    for satellite_name in satellite_names:
        data1_ = data1[satellite_name].pos
        data2_ = data2[satellite_name].pos
        loss = data1_ - data2_
        stats[satellite_name] = {}
        stats[satellite_name]["pre_x"] = np.sqrt(np.mean(loss[:, 0] ** 2))
        stats[satellite_name]["pre_y"] = np.sqrt(np.mean(loss[:, 1] ** 2))
        stats[satellite_name]["pre_z"] = np.sqrt(np.mean(loss[:, 2] ** 2))
        stats[satellite_name]["pre_3d"] = np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2))

    data1_ = np.vstack(
        [
            data1[satellite_name].pos for satellite_name in satellite_names
        ]
    )#.transpose()
    data2_ = np.vstack(
        [
           data2[satellite_name].pos for satellite_name in satellite_names
        ]
    )#.transpose()
    data_train, data_test, target_train, target_test = train_test_split(data1_, data2_, test_size=0.20, random_state=42)
    loss = target_test - data_test
    logger.info(" on validation dataset ")
    logger.info("INIT  -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
    helmert = HelmertTransform()
    helmert.fit(data_train, target_train)
    loss = target_test - helmert.apply(data_test)
    logger.info("FINAL -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
    
    for satellite_name in satellite_names:
        data1_ = helmert.apply(data1[satellite_name].pos)
        data2_ = data2[satellite_name].pos
        loss = data1_ - data2_
        stats[satellite_name]["post_x"] = np.sqrt(np.mean(loss[:, 0] ** 2))
        stats[satellite_name]["post_y"] = np.sqrt(np.mean(loss[:, 1] ** 2))
        stats[satellite_name]["post_z"] = np.sqrt(np.mean(loss[:, 2] ** 2))
        stats[satellite_name]["post_3d"] = np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2))
    # plt.savefig("helmert.png")
    satellite_names.sort()
    return helmert, stats

if __name__ == "__main__":
    main()