"""

Name: Grain Size Distribution Tool
Purpose: Find the average size of gravel in a stream network

Author: Braden Anderson
Created: 31 March 2017
Last Update: 31 March 2017

"""

import arcpy
from Reach import Reach

def main(dem,
         streamNetwork,
         precipMap):
    """Source code for our tool"""
    arcpy.env.overwriteOutput = True

    reachArray = makeReaches(dem, streamNetwork, precipMap)

    q_2 = findQ_2()


def makeReaches(dem, streamNetwork, precipMap):
    """Creates a series of reaches """
    reaches = []
    polylineCursor = arcpy.da.SearchCursor(streamNetwork, ['SHAPE@', 'SHAPE@XY'])

    for polyline in polylineCursor:
        width = findWidth(dem, precipMap)
        q_2 = findQ_2()
        reach = Reach(width, q_2, polyline[0], polyline[1])

        reaches.append(reach)

    return reaches


def findQ_2():
    """Returns the value of a two year flood event"""
    #TODO: Write findQ_2()
    i = 1  # placeholder
    return i


def findWidth(dem, precipMap):
    #TODO: Write findWidth()
    i = 1  # placeholder
    return i


if __name__ == '__main__':
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3])