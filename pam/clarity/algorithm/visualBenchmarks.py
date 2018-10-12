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


if( __name__ == "__main__"):
    argParser = argparse.ArgumentParser(description="An approximated implementation for the proposed algorithm.")
    argParser.add_argument("input", type=file, help="The input file.")
    argParser.add_argument("output", help="The output directory.")
    args = argParser.parse_args()

    imageStack = imread(args.input.name)

    fig = plt.figure()
    ax = fig.add_subplot(1,3,1)
    ahelp = fig.add_subplot(1,3,2)
    ax2 = fig.add_subplot(1,3,3)
    fig.hold(True)

    fd, hog_image = feature.hog(imageStack[0], orientations=16, pixels_per_cell=(2, 2),
                        cells_per_block=(4, 4), visualise=True)

    #blobs = feature.blob_log(imageStack[0], max_sigma=10, num_sigma=5, threshold=.08, overlap=1)

    #gradient = rank.gradient((imageStack[0]>150)*imageStack[0], morphology.disk(1))

    #markers = (imageStack[0]>180)
    #for i,blob in enumerate(blobs):
    #    markers[blob[0]][blob[1]] = i+2

    ax.imshow((hog_image>40)*imageStack[0])
    #ax.imshow(morphology.watershed(gradient, ndi.label(markers)[0]))
    #ahelp.imshow((imageStack[0]>180))
    ahelp.imshow(hog_image)
    ax2.imshow(imageStack[0])
    #ax2.plot(blobs[:,1],blobs[:,0],'w.')

    gradientStack = imageStack.copy()
    contourStack = imageStack.copy()
    threshholdStack = imageStack.copy()
    blobStack = imageStack.copy()

    for imageNum in range(0,imageStack.shape[0]):
        # find contours
        image = rank.mean_bilateral(imageStack[imageNum],morphology.disk(5))
        contours = measure.find_contours(image, 200)
        for c in contours:
            Z = np.ndarray(shape=(len(c[:,0])))
            Z.fill(imageNum)
            if c[0,0] == c[-1,0] and c[0,1] == c[-1,1] :
                for i in range(0,c.shape[0]):
                    contourStack[imageNum][c[i,0],c[i,1]] = 0

        #gradient
        gradientStack[imageNum] = rank.gradient(image, morphology.disk(1))

        #threshhold
        threshholdStack[imageNum] = (image>180)*255

        #blobs
        blobs = feature.blob_log(image, max_sigma=10, num_sigma=5, threshold=.09, overlap=1)
        for blob in blobs:
            x,y,r = blob
            blobStack[imageNum][x,y] = 0



    imsave(args.output+'gradient.tif',gradientStack)
    imsave(args.output+'threshhold.tif',threshholdStack)
    imsave(args.output+'blob.tif',blobStack)
    imsave(args.output+'contour.tif',contourStack)

    fig.show()
    plt.show()
