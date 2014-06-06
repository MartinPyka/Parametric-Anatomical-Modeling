"""Gauss 2D Kernel Module"""

import math


def gauss(uv, guv, *args):
    """Gauss-function for 2d
    u, v    : coordinates, to determine the function value
    vu, vv  : variance for both dimensionsj
    su, sv  : shift in u and v direction
    """
    vu = args[0][0]
    vv = args[0][1]
    su = args[0][2]
    sv = args[0][3]

    ruv = guv - uv  # compute relative position

    return math.exp(-((ruv[0] + su) ** 2 / (2 * vu ** 2) +
                    (ruv[1] + sv) ** 2 / (2 * vv ** 2)))


def gauss_vis(x, y, origin_x, origin_y, var_x, var_y):
    """Computes distribution value in two dimensional gaussian kernel"""
    return math.exp(-((x - origin_x) ** 2 / (2 * var_x ** 2) +
                      (y - origin_y) ** 2 / (2 * var_y ** 2)))


# TODO(SK): missing docstring
def unity(uv, guv, *args):
    return 1
