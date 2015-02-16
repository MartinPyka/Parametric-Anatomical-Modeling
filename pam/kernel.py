"""Kernel Module"""

import math


KERNEL_TYPES = [
    ("gauss", "Gauss", "", 1),
    ("gauss_u", "Gauss Line [u]", "", 2),
    ("gauss_v", "Gauss Line [v]", "", 3),
    ("unity", "Unity", "", 4),
]


def gauss(uv, guv, var_u=1.0, var_v=1.0, shift_u=0.0, shift_v=0.0, ):
    """Computes distribution value in two dimensional gaussian kernel"""
    ruv = guv - uv  # compute relative position

    return math.exp(-((ruv[0] + shift_u) ** 2 / (2 * var_u ** 2) +
                    (ruv[1] + shift_v) ** 2 / (2 * var_v ** 2)))    


# TODO(SK): missing docstring
def gauss_u(u, v, origin_u=0.0, var_u=1.0):
    return math.exp(-(1 / 2) * ((u - origin_u) / var_u) ** 2)


# TODO(SK): missing docstring
def gauss_v(u, v, origin_v=0.0, var_v=1.0):
    return math.exp(-(1 / 2) * ((v - origin_v) / var_v) ** 2)


# TODO(SK): missing docstring
def unity(u, v, origin_u, origin_v):
    return 1
