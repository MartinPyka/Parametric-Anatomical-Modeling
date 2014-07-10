"""Constants"""

import mathutils

# config files with many hard-coded variables, used in
# in other parts of PAM, primarily in pam.py

# key-values for the mapping-procedure
MAP_euclid = 0
MAP_normal = 1
MAP_random = 2
MAP_top = 3

DIS_euclid = 0
DIS_euclidUV = 1
DIS_jumpUV = 2
DIS_normalUV = 3
DIS_UVnormal = 4

# length of a ray along a normal-vector.
# This is used for 1pam.map3dPointToUV() and
# pam.map3dPointTo3d() to map points along the normal between two layers
RAY_FAC = 0.3

INTERPOLATION_QUALITY = 10

DEFAULT_LOCATION = mathutils.Vector((0.0, 0.0, 0.0))
DEFAULT_SCALE = mathutils.Vector((1.0, 1.0, 1.0))
DEFAULT_ROTATION = mathutils.Euler((0.0, 0.0, 0.0), "XYZ")

DEFAULT_RESOLUTION = 0.05
KERNEL_THRESHOLD = 0.05
