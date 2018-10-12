
#**** Import **************************************************************


from tifffile import *
import numpy as np

import argparse



# copy a subvolume out of a volume
def reduce( img, xBegin, yBegin, zBegin, width, height, depth  ):
    newImg = np.zeros((depth,height,width), dtype=np.uint8)

    for z in range(depth):
        for y in range(height):
            for x in range(width):
                newImg[z-1][y-1][x-1] = img[z-1][yBegin+y][xBegin+x]

    return newImg




if (__name__ == "__main__"):
    argParser = argparse.ArgumentParser(description="Extract a subvolume out of a tiff file.")
    argParser.add_argument("input", type=file, help="The input file.")
    argParser.add_argument("output", help="The output file's name.")
    argParser.add_argument("x", type=int)
    argParser.add_argument("y", type=int)
    argParser.add_argument("z", type=int)
    argParser.add_argument("width", type=int)
    argParser.add_argument("height", type=int)
    argParser.add_argument("depth", type=int)

    args = argParser.parse_args()

    # simply open the file, reduce it and save back to disk
    img = imread(args.input.name, key = range(args.z, args.z+args.depth))
    newImg = reduce( img, args.x, args.y, args.z, args.width, args.height, args.depth )
    imsave(args.output, newImg)
