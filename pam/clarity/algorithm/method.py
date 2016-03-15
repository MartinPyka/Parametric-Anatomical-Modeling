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
    for offsetZ in [-1,0,1]:
        for offsetY in [-1,0,1]:
            for offsetX in [-1,0,1]:
                curZ = z+offsetZ
                curY = y+offsetY
                curX = x+offsetX
                #if not(volume[curZ][curY][curX] == 0) and not(volume[curZ][curY][curX] == id):
                    #color_neuron(volume, curX, curY, curZ, id)
                if not(volume[curZ][curY][curX] == 0):
                    volume[curZ][curY][curX] = id


# this is not exactly the proposed method since the test data differs too much
def example_method( volume ):

    print('Preprocess volume...')
    label_offset = 0
    for imageNum in range(0,volume.shape[0]):
        print('Processing slice ' + str(imageNum+1) + '/' + str(volume.shape[0]))

        # difference of gaussian detects neuron blobs
        image_dog = ndi.gaussian_filter(volume[imageNum], .5) - ndi.gaussian_filter(volume[imageNum], 1)

        # remove background
        image = np.bitwise_and(image_dog>10, image_dog<240)

        # make the neurons bigger, so they give a neuron mask to detect the neuron shape
        neuron_mask = morphology.dilation(image)

        # remove potential neurons at the border, they are handled separately
        image = segmentation.clear_border(neuron_mask)

        # first pass, label all areas (neurons) independently
        volume[imageNum],offadd = measure.label(image, return_num=True)

        # adjust labels.....the slow way
        for y in range(1,volume.shape[1]-1):
            for x in range(1,volume.shape[2]-1):
                if not(volume[imageNum][y][x] == 0):
                    volume[imageNum][y][x] = volume[imageNum][y][x] + label_offset

        # adjust label offset
        label_offset = label_offset + offadd


    #imsave('intermediate-1.tif',volume)


    # NOTE THIS CODE BELOW IS JUST FOR TESTING PURPOSES! THE PERFORMANCE IS ACTUALLY TERRIBLE!

    # group neurons between layers together....
    #TODO optimize this step
    print('Connecting layers...')

    for z in range(1,volume.shape[0]-1):
        print('Processing slice ' + str(z) + '/' + str(volume.shape[0]-2))
        for y in range(1,volume.shape[1]-1):
            for x in range(1,volume.shape[2]-1):
                # we got a neuron
                if not(volume[z][y][x] == 0):
                    color_neuron(volume,x,y,z,volume[z][y][x])


    #imsave('intermediate-2.tif',volume)

    # get the neuron coordinates .. the slow way
    #TODO optimize this step
    print('Extract neuron positions...')

    skipme = []
    positions = []
    for z in range(1,volume.shape[0]-1):
        print('Processing slice ' + str(z) + '/' + str(volume.shape[0]-2))

        for y in range(1,volume.shape[1]-1):
            for x in range(1,volume.shape[2]-2):
                # skip background for the sake of performance
                if not(volume[z][y][x] == 0):
                    if not(volume[z][y][x] in skipme):
                        skipme.append(volume[z][y][x])
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
    imageStack = imread(args.input.name).astype(np.uint16)

    start = time.time( )
    positions = example_method( imageStack )
    stop = time.time( )
    print("The current implementation took "+str(stop-start)+" seconds to finish.")

    with open(args.output,'wb') as f:
        coordWriter = csv.writer(f, delimiter=';')
        coordWriter.writerow(positions)
