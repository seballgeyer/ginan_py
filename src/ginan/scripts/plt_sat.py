import argparse

import matplotlib.pyplot as plt
import numpy as np

from ginan.data.satellite import satellite
from ginan.dbconnector import mongo

plt.style.use(['seaborn-ticks', 'seaborn-paper'])
def plot(args):
    db = mongo.MongoDB(url=args.db, data_base=args.coll)
    satG01 = satellite(db, sat=args.sat)
    satG01.get_postfit()
    rms = satG01.get_rms()
    print(f"{args.coll} {arg.sat}   {np.array2string(rms[:3], precision=6, floatmode='fixed')}  => {rms[3]:.6f}")
    satG01.get_state()
    fig, ax = plt.subplots(nrows=3)
    if (args.to_rac):
        r = satG01.rac()
        ylabel = ["r", "a", "c"]
    else:
        r = satG01.residual.transpose()
        ylabel = ["x", "y", "z"]

    for a, d in zip(ax, r):
        a.plot(satG01.time, d)
    for a, l in zip(ax, ylabel):
        a.set_ylabel(l)
    plt.savefig(f"plt_{args.coll}_{args.sat}.pdf", bbox_inches='tight')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=__file__,
        description='Plot satellite related fittings',
        epilog='Text at the bottom of help')
    parser.add_argument('--db', default='127.0.0.1', type=str)
    parser.add_argument('--coll', type=str, required=True)
    parser.add_argument('-s', '--sat', type=str, required=True)
    parser.add_argument('-r', '--residual', action='store_true', default=False)
    parser.add_argument('--to_rac', action='store_true', default=False)
    arg = parser.parse_args()
    plot(arg)
