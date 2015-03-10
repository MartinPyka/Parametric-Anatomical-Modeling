"""Kernel Module"""

import math
import numpy as np


KERNEL_TYPES = [
    ("gauss", "Gauss", "", 0),
    ("stripe_with_end", "Stripe with end", "", 1),
    ("unity", "Unity", "", 2)
]


def gauss(uv, guv, var_u=1.0, var_v=1.0, shift_u=0.0, shift_v=0.0, ):
    """Computes distribution value in two dimensional gaussian kernel"""
    ruv = guv - uv  # compute relative position

    return math.exp(-((ruv[0] + shift_u) ** 2 / (2 * var_u ** 2) +
                    (ruv[1] + shift_v) ** 2 / (2 * var_v ** 2)))

#######################################################################
## copied from:
## http://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
#######################################################################

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
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

#######################################################################
## end of copy
#######################################################################


def stripe_with_end(uv, guv, 
                    vec_u=1., vec_v=0., 
                    shift_u = 0., shift_v = 0., 
                    var_v = 0.2):
    """ The kernel is essiantially a stripe along the (vec_u, vec_v) axis
    but everything in the negative direction of the vector is ommitted. This
    function is helpful to model axons which grow only in one direction
    uv    : position of the neuron
    guv    : relativ position 
    vec_u   : u-component of the direction vector
    shift_u : shift along the u-direction relativ in space of [vec_u, vec_v]
    shift_v : shift along the v-direction  [vec_u, vec_v]
    var_v    : width of the kernel """
    
    # angle of standard-vector to base
    ruv = guv - uv
    
    vec = np.array([vec_u, vec_v])
    angle = angle_between(vec, np.array([1., 0.]))
    rotMatrix = np.array([[np.cos(-angle), -np.sin(-angle)], 
                             [np.sin(-angle),  np.cos(-angle)]])
    rot_vec = np.dot( rotMatrix, np.array(ruv) )
    rot_vec[0] = rot_vec[0] - shift_u
    rot_vec[1] = rot_vec[1] - shift_v
    if (rot_vec[0] < 0):
        return 0
    else:
        return math.exp(-(rot_vec[1] ** 2 / (2*var_v**2)))


# TODO(SK): missing docstring
def gauss_u(u, v, origin_u=0.0, var_u=1.0):
    return math.exp(-(1 / 2) * ((u - origin_u) / var_u) ** 2)


# TODO(SK): missing docstring
def gauss_v(u, v, origin_v=0.0, var_v=1.0):
    return math.exp(-(1 / 2) * ((v - origin_v) / var_v) ** 2)


# TODO(SK): missing docstring
def unity(u, v, origin_u, origin_v):
    return 1
