# config files with many hard-coded variables, used in
# in other parts of PAM, primarily in pam.py

# some key-values for the mapping-procedure
MAP_euclid= 0
MAP_normal = 1
MAP_random = 2
MAP_top = 3

DIS_euclid = 0
DIS_normalUV = 1
DIS_euclidUV = 2

# length of a ray along a normal-vector. This is used for pam.map3dPointToUV() and 
# pam.map3dPointTo3d() to map points along the normal between two layers
ray_fac = 1.02