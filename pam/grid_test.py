import unittest
import grid
import kernel
import numpy as np
import cProfile

N = 5000

def testGrid():
    np.random.seed(42)
    g = grid.UVGrid(3)
    print("Computing pre mask")
    g.compute_post_mask(kernel.gauss, [1.0, 1.0, 0.0, 0.0])
    print("Inserting post neurons")
    uvs = np.random.rand(N, 2)
    for uv in uvs:
        g.insert_postNeuron(1, uv, (1., 2., 3.), 42)

    print("Computing pre mask")
    g.compute_pre_mask(kernel.gauss, [1.0, 1.0, 0.0, 0.0])
    print("selecting")
    # for i in range(N/10):
    g.select_random((0.0, 0.0), N)

cProfile.run('testGrid()')