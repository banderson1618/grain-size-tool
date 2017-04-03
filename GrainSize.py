"""

Name: Grain Size Distribution Tool
Purpose: Find the average size of gravel in a stream network

Author: Braden Anderson
Created: 31 March 2017
Last Update: 31 March 2017

"""

import arcpy


def main(dem,
         streamNetwork,
         precipMap):
    """Source code for our tool"""
    arcpy.env.overwriteOutput = True

    makeReaches(streamNetwork)
    q_2 = findQ_2()
    width = findWidth(dem, precipMap)

    arcpy.AddMessage(dem)


if __name__ == '__main__':
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3])