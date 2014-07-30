"""Gauss 2D Kernel Module"""

import math


def gauss(uv, guv, *args):
    """Gauss-function for 2d
    uv      : center of the gauss-bell
    guv     : point for which the function value should be computed
    args    : variance and shift parameter
    """
    vu = args[0][0]   # variance in u
    vv = args[0][1]   # variance in v
    su = args[0][2]   # shift in u
    sv = args[0][3]   # shift in v

    ruv = guv - uv  # compute relative position

    return math.exp(-((ruv[0] + su) ** 2 / (2 * vu ** 2) +
                    (ruv[1] + sv) ** 2 / (2 * vv ** 2)))


def gauss_u(uv, guv, *args):
    """ Gauss-function that create a gauss-line
    along the u-coordinate
    uv      : center of the gauss-bell
    guv     : point for which the function value should be computed
    args    : variance and shift parameter for u
    """
    vu = args[0][0]   # variance in u
    su = args[0][1]   # shift in u

    ruv = guv - uv  # compute relative position

    return math.exp(-(1 / 2) * ((ruv[1] + su) / vu) ** 2)


def gauss_v(uv, guv, *args):
    """ Gauss-function that create a gauss-line
    along the v-coordinate
    uv      : center of the gauss-bell
    guv     : point for which the function value should be computed
    args    : variance and shift parameter for v
    """
    vv = args[0][0]   # variance in u
    sv = args[0][1]   # shift in u

    ruv = guv - uv  # compute relative position

    return math.exp(-(1 / 2) * ((ruv[0] + sv) / vv) ** 2)


def gauss_vis(u, v, origin_u=0.0, origin_v=0.0, var_u=1.0, var_v=1.0):
    """Computes distribution value in two dimensional gaussian kernel"""
    return math.exp(-((u - origin_u) ** 2 / (2 * var_u ** 2) +
                      (v - origin_v) ** 2 / (2 * var_v ** 2)))


# TODO(SK): missing docstring
def unity(uv, guv, *args):
    return 1
