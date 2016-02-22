import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

import numpy as np

from tifffile import *

from skimage import data, color, exposure
from skimage.util import img_as_ubyte
from skimage.filters import gabor_kernel

from scipy import ndimage as ndi

import argparse


# try frequency filtering to remove the inteference-style noise
if (__name__ == "__main__"):
    argParser = argparse.ArgumentParser(description="Visually benchmark gabor filtering on a sample.")
    argParser.add_argument("input", type=file, help="The input file.")
    argParser.add_argument("frequency", type=float, help="Gabor filter frequency.")
    argParser.add_argument("theta", type=float, help="Gabor filter theta.")
    argParser.add_argument("sigma_x", type=float, help="Gabor filter sigma-x.")
    argParser.add_argument("sigma_y", type=float, help="Gabor filter sigma-y.")

    args = argParser.parse_args()

    imageStack = imread(args.input.name)

    #initialize visualization with 3 plots
    fig = plt.figure()
    ax = fig.add_subplot(1,3,1)
    original = fig.add_subplot(1,3,2)
    helper = fig.add_subplot(1,3,3)
    fig.hold(True)

    freqSpace = np.fft.fft2(imageStack[0])

    ax.imshow(np.log(np.abs(np.fft.fftshift(freqSpace))**2),cmap=plt.cm.gray)
    original.imshow(imageStack[0])
    helper.imshow(ndi.convolve(imageStack[0], gabor_kernel(args.frequency, theta=args.theta, sigma_x=args.sigma_x, sigma_y=args.sigma_y), mode='wrap'))

    fig.show()
    plt.show()
