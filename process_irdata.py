from os import path
import glob
import pandas as pd
import numpy as np


pulse_width = 1 / 38e3 * 1e6
a, b = 3.65315577, -119.51208862


def normalize(x, gap=200):
    sx = np.sort(x)
    m = np.round([a.mean() for a in np.split(sx, np.where(np.diff(sx) > gap)[0] + 1)]).astype(int)
    index = np.argmin(np.abs(np.subtract.outer(x, m)), axis=1)
    return m[index]


def process_irdata(filename):
    df = pd.read_csv(filename)
    df.columns = ["t", "c"]

    dt = np.round(np.diff(df.t.values)[1:] * 1e6).astype(np.int)
    v = df.c.values[1:-1]

    arr = np.r_[dt, 1000000].reshape(-1, 2)
    arr[:, 0] = normalize(arr[:, 0])
    arr[:, 1] = normalize(arr[:, 1])

    arr2 = np.zeros_like(arr)
    arr2[:, 0] = np.round(arr[:, 0] / pulse_width)
    arr2[:, 1] = np.round((a * arr[:, 1] + b) * 0.1)
    arr2[-1, 1] = 100

    arr2.ravel().astype(np.uint16).tofile(path.splitext(filename)[0] + ".bin")


def main():
    for fn in glob.glob("irdata/*.csv"):
        print("processing {}".format(fn))
        process_irdata(fn)


if __name__ == '__main__':
    main()