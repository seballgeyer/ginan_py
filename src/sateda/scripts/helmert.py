import argparse
import os
import logging
import sys

import numpy as np

from sateda.io.sp3 import sp3
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)

def helmert(coeffs, vector):
    translate = np.array(coeffs[:3])
    scale = coeffs[3]
    angle = np.array(coeffs[4:])
    #convert angle from  micro arcseconds to radians
    rotation_matrix = np.array([
        [1, -angle[2], angle[1]],
        [angle[2], 1, -angle[0]],
        [-angle[1], angle[0], 1]
    ])
    # rotated = np.einsum('ijk,jk->ik', rotation_matrix[:, :, np.newaxis], vector)
    rotated = np.zeros_like(vector)
    for i in range(rotated.shape[0]):
        rotated[i,:] = rotation_matrix @ vector[i,:] * (1+scale) + translate
    # return translate[:,  np.newaxis] + (1+ scale) * rotated
    return rotated

def helmert_jac(coeffs, vector):
    jac = np.zeros((vector.shape[0]*vector.shape[1], len(coeffs)))
    translate = np.array(coeffs[:3])
    scale = coeffs[3]
    angle = np.array(coeffs[4:])
    rotation_matrix = np.array([
        [1, -angle[2], angle[1]],
        [angle[2], 1, -angle[0]],
        [-angle[1], angle[0], 1]
    ])
    for i in range(vector.shape[0]):
        jac[i*vector.shape[1]:(i+1)*vector.shape[1],:3] = np.eye(3)
        jac[i*vector.shape[1]:(i+1)*vector.shape[1],3] = rotation_matrix @ vector[i,:]
        jac[i*vector.shape[1]:(i+1)*vector.shape[1],4:] = np.array([
            [0, vector[i,2], -vector[i,1]],
            [-vector[i,2], 0, vector[i,0]],
            [vector[i,1], -vector[i,0], 0]
        ]) * (1+scale)
    return jac

def helmert_residuals(coeffs, vector, target):
    loss = target - helmert(coeffs, vector)
    loss2 = np.zeros(loss.shape[0]*loss.shape[1])
    for idx, l in enumerate(loss):
        loss2[idx*loss.shape[1]:(idx+1)*loss.shape[1]] = l
    return loss2


def parse_args():
    #print current directory
    print(os.getcwd())
    args = argparse.ArgumentParser("Helmert transformation")
    args.add_argument("input1", help="Input file")
    args.add_argument("input2", help="Input file2")
    args.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    args.add_argument("-r", "--rotate", action="store_true", help="Rotate the data")
    args.add_argument("-o", "--output", help="Output file")

    args = args.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return args

def main():
    args = parse_args()
    data1 = sp3.read(file_or_string=args.input1)
    data2 = sp3.read(file_or_string=args.input2)
    # data1 and data2 are sp3 objects assumed to have the same data. data1.data is a dictionary mapping a vector.
    # stack all data1 information into a single vector. data1.data[satellite_name].time is a numpy vector
    time = np.hstack([data1.data[satellite_name]['time'] for satellite_name in data1.data.keys()])
    #create a vector 3 * len(time)  for data 1 and data2. first comulmn is "x", second is "y", third is "z"
    satellite_names = list(data1.data.keys())  # Assuming data1 and data2 have the same keys
    data1 = np.hstack([
        np.vstack([data1.data[satellite_name]["x"],
                   data1.data[satellite_name]["y"],
                   data1.data[satellite_name]["z"]])
        for satellite_name in satellite_names
    ]).transpose()
    data2 = np.hstack([
        np.vstack([data2.data[satellite_name]["x"],
                   data2.data[satellite_name]["y"],
                   data2.data[satellite_name]["z"]])
        for satellite_name in satellite_names
    ]).transpose()
    print(data1.shape, data2.shape, time.shape)
    # split data1 and data2 in a train and test set (80, 20%), same index for both
    idx = np.random.permutation(len(time))
    idx_train = idx[:int(0.8*len(time))]
    idx_test = idx[int(0.8*len(time)):]
    # data1_train = data1[idx_train,:]
    # data2_train = data2[idx_train,:]
    model = np.zeros(7)
    converged = False
    logger.info("Starting the minibatch")
    logger.info("train size: % 4d test size: % 4d", len(idx_train), len(idx_test))
    i = 1

    loss = data1[idx_test, :] - data2[idx_test, :]
    logger.info("INIT-> residual %e",  np.sqrt(np.mean(np.linalg.norm(loss, axis=1) ** 2)))
    # while not converged:
    while i < 50:
        #shuffle the train data
        np.random.shuffle(idx_train)
        for batch in np.array_split(idx_train, len(idx_train)//256):
            #create the design matrix
            design_matrix = helmert_jac(model, data1[batch,:])
            residual = helmert_residuals(model, data1[batch,:], data2[batch,:])
            #solve the least square problem
            delta = np.linalg.inv(design_matrix.transpose() @ design_matrix) @ design_matrix.transpose() @ residual
            #update the model
            model += delta
            # logger.info("batch size: % 4d", len(batch))
            # logger.info("model: %s", model)
        # residual = helmert_residuals(model, data1[idx_test, :], data2[idx_test, :])

        # logger.info('model %s', np.array2string(model))
        loss = helmert(model, data1[idx_test, :]) - data2[idx_test, :]
        logger.info("iteration: % 4d -> residual %e", i, np.sqrt(np.mean(np.linalg.norm(loss, axis=1)**2)))
        # print(np.sqrt(np.mean(np.linalg.norm(loss, axis=1)**2)))
        # logging.info('residual: %e', np.sqrt(np.mean(np.linalg.norm(loss, axis=1)**2)))
        # loss = helmert(model*0.0, data1[idx_test, :]) - data2[idx_test, :]
        # print(', ...., ', np.sqrt(np.mean(np.linalg.norm(loss, axis=1)**2)))
        # break
        # print("residual: ", np.linalg.norm(residual))
        converged=True
        i+=1








    pass

if __name__ == "__main__":
    main()
