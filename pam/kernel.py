"""Kernel Module"""

import math
import numpy as np


KERNEL_TYPES = [
    ("gauss", "Gauss", "", 0),
    ("gauss_u", "Gauss (u)", "", 1),
    ("gauss_v", "Gauss (v)", "", 2),
    ("stripe_with_end", "Stripe with end", "", 3),
    ("unity", "Unity", "", 4)
]


# TODO(SK): Fill in docstring parameter/return value
def gauss(uv, guv, var_u=1.0, var_v=1.0, shift_u=0.0, shift_v=0.0):
    """Computes distribution value in two dimensional gaussian kernel

    :param uv: uv coordinates
    :type uv: tuple (float, float)
    :param guv:
    :type guv: tuple (float, float)
    :param float var_u:
    :param float var_v:
    :param float shift_u:
    :param float shift_u:
    :return: gauss value at point uv in 2d space
    :rtype: float

    """
    ruv = guv - uv  # compute relative position

    return np.exp(-((ruv[...,0] + shift_u) ** 2 / (2 * var_u ** 2) +
                    (ruv[...,1] + shift_v) ** 2 / (2 * var_v ** 2)))


# copied from:
# http://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
def unit_vector(vector):
    """Returns the unit vector of the vector

    :param mathutils.Vector vector: a vector
    :return: unit vector
    :rtype: mathutils.Vector

    """
    return vector / np.linalg.norm(vector)


# copied from:
# http://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
def angle_between(v1, v2):
    """Returns the angle in radians between vectors `v1` and `v2`::

        >>> angle_between((1, 0, 0), (0, 1, 0))
        1.5707963267948966
        >>> angle_between((1, 0, 0), (1, 0, 0))
        0.0
        >>> angle_between((1, 0, 0), (-1, 0, 0))
        3.141592653589793

    :param mathutils.Vector v1: a vector
    :param mathutils.Vector v2: another vector
    :return: angle between vectors
    :rtype: float

    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if np.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        else:
            return np.pi
    return angle


# TODO(SK): Fill in docstring parameter/return value
def stripe_with_end(uv, guv, vec_u=1.0, vec_v=0.0, shift_u=0.0, shift_v=0.0,
                    var_v=0.2):
    """The kernel is essiantially a stripe along the (vec_u, vec_v) axis
    but everything in the negative direction of the vector is ommitted.

    This function is helpful to model axons which grow only in one direction

    :param uv: position of the neuron
    :param guv: relativ position
    :param float vec_u: u-component of the direction vector
    :param float vec_v: v-component of the direction vector
    :param float shift_u: shift along the u-direction relativ in space
    :param float shift_v: shift along the v-direction
    :param float var_v: width of the kernel
    :type uv: tuple (float, float)
    :type guv: tuple (float, float)
    :return:
    :rtype: float

    """

    # angle of standard-vector to base
    ruv = guv - uv

    vec = np.array([vec_u, vec_v])
    angle = angle_between(vec, np.array([1., 0.]))
    rotMatrix = np.array([
        [np.cos(-angle), -np.sin(-angle)],
        [np.sin(-angle), np.cos(-angle)]
    ])
    rot_vec = np.dot(rotMatrix, np.array(ruv))
    rot_vec[0] = rot_vec[0] - shift_u
    rot_vec[1] = rot_vec[1] - shift_v
    if (rot_vec[0] < 0):
        return 0.0
    else:
        return math.exp(-(rot_vec[1]**2 / (2 * var_v**2)))


# TODO(SK): Rephrase docstring & fill in parameter values
def gauss_u(uv, guv, origin_u=0.0, var_u=1.0):
    """Computes distribution value in one dimensional gaussian kernel
    in u direction

    :param uv: uv coordinates
    :type uv: tuple (float, float)
    :param guv:
    :type guv: tuple (float, float)
    :param float origin_u:
    :param float origin_v:
    :type origin_u:
    :type origin_v:
    :return: gauss value at point uv in 2d space
    :rtype: float

    """
    ruv = guv - uv  # compute relative position

    return math.exp(-(1 / 2) * ((ruv[0] - origin_u) / var_u) ** 2)


# TODO(SK): Rephrase docstring & fill in parameter values
def gauss_v(uv, guv, origin_v=0.0, var_v=1.0):
    """Computes distribution value in one dimensional gaussian kernel
    in v direction

    :param uv: uv coordinates
    :type uv: tuple (float, float)
    :param guv:
    :type guv: tuple (float, float)
    :param float origin_u:
    :param float origin_v:
    :type origin_u:
    :type origin_v:
    :return: gauss value at point uv in 2d space
    :rtype: float

    """
    ruv = guv - uv  # compute relative position

    return math.exp(-(1 / 2) * ((ruv[1] - origin_v) / var_v) ** 2)


# TODO(SK): Rephrase docstring & fill in parameter values
def unity(uv, guv, origin_u, origin_v):
    """Returns a unity kernel

    :param uv: uv coordinates
    :type uv: tuple (float, float)
    :param guv:
    :type guv: tuple (float, float)
    :param float origin_u:
    :param float origin_v:
    :type origin_u:
    :type origin_v:
    :return: 1.0
    :rtype: float

    """
    return 1.0