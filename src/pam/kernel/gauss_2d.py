"""Gauss 2D Kernel Module"""

import math


# TODO(MP): Kernel definition must be equal across code fragments
# TODO(MP): Kernel functions can moved to separate module
def post(uv, guv, *args):
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


# TODO(SK): missing docstring
def unity(u, v, *args):
    return 1
