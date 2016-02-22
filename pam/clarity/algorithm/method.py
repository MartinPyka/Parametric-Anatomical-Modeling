import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

import numpy as np

from skimage.external.tifffile import *

from skimage import data, color, exposure
from skimage.util import img_as_ubyte
from skimage import measure
from skimage import segmentation
from skimage import feature
from skimage import morphology
from skimage import filters
from skimage import exposure
from skimage.filters import rank

from scipy import ndimage as ndi

import argparse
import csv
import sys
import time

# bruteforce relabel in 3d
def color_neuron(volume, x,y,z, id):
    for offsetZ in [-1,1]:
        for offsetY in [-1,0,1]:
            for offsetX in [-1,0,1]:
                curZ = z+offsetZ
                curY = y+offsetY
                curX = x+offsetX
                if not(volume[curZ][curY][curX] == 0) and not(volume[curZ][curY][curX] == id):
                    #color_neuron(volume, curX, curY, curZ, id)
                    volume[curZ][curY][curX] = id


# this is not exactly the proposed method since the test data differs too much
def example_method( imageStack ):
    neurons = imageStack.copy( )
    for imageNum in range(0,imageStack.shape[0]):
        # difference of gaussian detects neuron blobs
        image_dog = ndi.gaussian_filter(imageStack[imageNum], .5) - ndi.gaussian_filter(imageStack[imageNum], 1)

        # remove background
        image = np.bitwise_and(image_dog>10, image_dog<240)

        # make the neurons bigger, so they give a neuron mask to detect the neuron shape
        neuron_mask = morphology.dilation(image)

        # remove potential neurons at the border, they are handled separately
        image = segmentation.clear_border(neuron_mask)

        # first pass, label all areas (neurons) independently
        neurons[imageNum] = measure.label(image)

        # second pass, extract borders
        #neuron_shapes = segmentation.find_boundaries(neurons,mode='inner').astype(np.uint8)


    # NOTE THIS CODE BELOW IS JUST FOR TESTING PURPOSES! THE PERFORMANCE IS ACTUALLY TERRIBLE!

    # group neurons between layers together....the slow way
    #TODO optimize this step
    for z in range(1,neurons.shape[0]-1):
        for y in range(1,neurons.shape[1]-1):
            for x in range(1,neurons.shape[2]-1):
                # we got a neuron
                if not(neurons[z][y][x] == 0):
                    color_neuron(neurons,x,y,z,neurons[z][y][x])

    # get the neuron coordinates .. the slow way
    #TODO optimize this step
    skipme = []
    positions = []
    for z in range(1,neurons.shape[0]-1):
        for y in range(1,neurons.shape[1]-1):
            for x in range(1,neurons.shape[2]-1):
                # skip background for the sake of performance
                if not(neurons[z][y][x] == 0):
                    if not(neurons[z][y][x] in skipme):
                        skipme.append(neurons[z][y][x])
                        positions.append((x,y,z))

    return positions


if( __name__ == "__main__"):
    argParser = argparse.ArgumentParser(description="An approximated implementation for the proposed algorithm.")
    argParser.add_argument("input", type=file, help="The input file.")
    argParser.add_argument("output", help="The output file.")
    argParser.add_argument("threads", type=int, help="Number of threads to work with.")
    argParser.add_argument("memory", type=int, help="The maximum amount of memory for this programm in mb.")
    args = argParser.parse_args()

    #pool = Pool(processes=args.threads)
    # read a [available working memory size]/ 2 /[number of threads] mb box for each thread
    # this results in
    # remember to leave some overlapping regions!
    imageStack = imread(args.input.name)

    start = time.time( )
    positions = example_method( imageStack )
    stop = time.time( )
    print("The current implementation took "+str(stop-start)+" seconds to finish.")

    #imsave(args.output,neurons.astype(np.uint32))

    with open(args.output,'wb') as f:
        coordWriter = csv.writer(f, delimiter=' ', quotechar='|')
        coordWriter.writerow(positions)
