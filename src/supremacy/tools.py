# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from . import config


def wrap_position(x, y):
    x = x % config.nx
    y = y % config.ny
    if x < 0:
        x = config.nx + x
    if y < 0:
        y = config.ny + y
    return x, y


def distance_on_plane(xa, ya, xb, yb):
    return np.sqrt((xb - xa)**2 + (yb - ya)**2)


def distance_on_torus(xa, ya, xb, yb):
    dx = np.abs(xb - xa)
    dy = np.abs(yb - ya)
    return np.sqrt(
        np.minimum(dx, config.nx - dx)**2 + np.minimum(dy, config.ny - dy)**2)


def periodic_distances(xa, ya, xb, yb):
    xc = xa + config.nx
    yc = ya + config.ny
    xl = np.array([xb, xb + config.nx, xb + 2 * config.nx] * 3)
    yl = np.array([yb] * 3 + [yb + config.ny] * 3 + [yb + 2 * config.ny] * 3)
    d = np.sqrt((xl - xc)**2 + (yl - yc)**2)
    return d, xl, yl


class ReadOnly:

    def __init__(self, props):
        for key, item in props.items():
            setattr(self, key, item)
