import argparse
import os
import logging
import sys

import json
import numpy as np

from sateda.io.sp3 import sp3, sp3_align


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)


def helmert(coeffs, vector):
    translate = np.array(coeffs[:3])
    scale = coeffs[3]
    angle = np.array(coeffs[4:])
    # convert angle from  micro arcseconds to radians
    rotation_matrix = np.array([[1, -angle[2], angle[1]], [angle[2], 1, -angle[0]], [-angle[1], angle[0], 1]])
    # rotated = np.einsum('ijk,jk->ik', rotation_matrix[:, :, np.newaxis], vector)
    rotated = np.zeros_like(vector)
    for i in range(rotated.shape[0]):
        rotated[i, :] = rotation_matrix @ vector[i, :] * (1 + scale) + translate
    # return translate[:,  np.newaxis] + (1+ scale) * rotated
    return rotated


def helmert_jac(coeffs, vector):
    jac = np.zeros((vector.shape[0] * vector.shape[1], len(coeffs)))
    translate = np.array(coeffs[:3])
    scale = coeffs[3]
    angle = np.array(coeffs[4:])
    rotation_matrix = np.array([[1, -angle[2], angle[1]], [angle[2], 1, -angle[0]], [-angle[1], angle[0], 1]])
    for i in range(vector.shape[0]):
        jac[i * vector.shape[1] : (i + 1) * vector.shape[1], :3] = np.eye(3)
        jac[i * vector.shape[1] : (i + 1) * vector.shape[1], 3] = rotation_matrix @ vector[i, :]
        jac[i * vector.shape[1] : (i + 1) * vector.shape[1], 4:] = np.array(
            [[0, vector[i, 2], -vector[i, 1]], [-vector[i, 2], 0, vector[i, 0]], [vector[i, 1], -vector[i, 0], 0]]
        ) * (1 + scale)
    return jac


def helmert_residuals(coeffs, vector, target, flatten=True):
    losses = target - helmert(coeffs, vector)
    if flatten:
        return losses.flatten()
    return losses


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
    # split data1 and data2 in a train and test set (80, 20%), same index for both
    idx_train, idx_test = split_train_test(time, ratio=0.8)
    model = np.zeros(7)
    converged = False
    logger.info("Starting the minibatch")
    logger.info("train size: % 4d test size: % 4d", len(idx_train), len(idx_test))
    i = 1

    loss = data1_[idx_test, :] - data2_[idx_test, :]
    logger.info("INIT -> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
    # while not converged:
    while i < 50:
        # shuffle the train data
        np.random.shuffle(idx_train)
        for batch in np.array_split(idx_train, len(idx_train) // 256):
            # create the design matrix
            design_matrix = helmert_jac(model, data1_[batch, :])
            residual = helmert_residuals(model, data1_[batch, :], data2_[batch, :])
            # solve the least square problem
            delta = np.linalg.inv(design_matrix.transpose() @ design_matrix) @ design_matrix.transpose() @ residual
            # update the model
            model += delta
            # logger.info("batch size: % 4d", len(batch))
            # logger.info("model: %s", model)
        # residual = helmert_residuals(model, data1[idx_test, :], data2[idx_test, :])

        # logger.info('model %s', np.array2string(model))
        loss = helmert(model, data1_[idx_test, :]) - data2_[idx_test, :]
        logger.debug("iteration: % 4d -> residual %e", i, np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
        # print(np.sqrt(np.mean(np.linalg.norm(loss, axis=1)**2)))
        # logging.info('residual: %e', np.sqrt(np.mean(np.linalg.norm(loss, axis=1)**2)))
        # loss = helmert(model*0.0, data1[idx_test, :]) - data2[idx_test, :]
        # print(', ...., ', np.sqrt(np.mean(np.linalg.norm(loss, axis=1)**2)))
        # break
        # print("residual: ", np.linalg.norm(residual))
        converged = True
        i += 1

    loss = helmert(model, data1_[:, :]) - data2_[:, :]
    logger.info("FINAL-> residual %e", np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
    for satellite_name in satellite_names:
        data1_ = np.vstack(
            [data1.data[satellite_name]["x"], data1.data[satellite_name]["y"], data1.data[satellite_name]["z"]]
        ).transpose()

        data2_ = np.vstack(
            [data2.data[satellite_name]["x"], data2.data[satellite_name]["y"], data2.data[satellite_name]["z"]]
        ).transpose()

        loss = helmert(model, data1_) - data2_
        stats[satellite_name]["post_x"] = np.sqrt(np.mean(loss[:, 0] ** 2))
        stats[satellite_name]["post_y"] = np.sqrt(np.mean(loss[:, 1] ** 2))
        stats[satellite_name]["post_z"] = np.sqrt(np.mean(loss[:, 2] ** 2))
        stats[satellite_name]["post_3d"] = np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2))

    satellite_names.sort()
    logger.info("       pre_x     pre_y     pre_z    pre_3d     post_x    post_y    post_z   post_3d")
    for d in satellite_names:
        data = stats[d]
        logger.info(
            f"{d}: "
            f"{data['pre_x']: .6f} {data['pre_y']: .6f} {data['pre_z']: .6f} {data['pre_3d']: .6f} "
            f"{data['post_x']: .6f} {data['post_y']: .6f} {data['post_z']: .6f} {data['post_3d']: .6f} "
        )
    logger.info(f" Estimated parameters:\n" f"   T: {model[:3]}\n" f"   R: {model[4:]}\n" f"   S: {model[3]}")
    pass


def split_train_test(time, ratio=0.8):
    data_length = len(time)
    split = int(ratio * data_length)
    idx = np.random.permutation(data_length)
    idx_train = idx[:split]
    idx_test = idx[split:]
    return idx_train, idx_test


if __name__ == "__main__":
    main()
