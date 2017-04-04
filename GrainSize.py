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
    arcpy.CheckOutExtension("Spatial")

    reachArray = makeReaches(dem, streamNetwork, precipMap)

    #for i in range(1, 2880, 2880):
    #    arcpy.AddMessage(reachArray[i].xyPosition)
    arcpy.AddMessage(reachArray[0].xyPosition)
    arcpy.AddMessage(reachArray[2888].xyPosition)

    q_2 = findQ_2()


def makeReaches(dem, streamNetwork, precipMap):
    """Creates a series of reaches """
    # TODO: Fix the reach's xy coordinates being wrong
    reaches = []
    polylineCursor = arcpy.da.SearchCursor(streamNetwork, ['SHAPE@', 'SHAPE@XY'])
    cursor = arcpy.da.InsertCursor(streamNetwork, ['SHAPE@'])
    flowDirection = arcpy.sa.FlowDirection(dem) # Placing this here to pass it to findWidth()
    flowAccumulation = arcpy.sa.FlowAccumulation(flowDirection)

    arcpy.env.workspace = "C:\Users\A02150284\Documents\ArcGIS\TestMapData"
    arcpy.MakeFeatureLayer_management("NHD_Asotin_all_segmeneted.shp", "polylines_lyr")
    arcpy.SaveToLayerFile_management("polylines_lyr", "C:\Users\A02150284\Documents\ArcGIS\TestMapData\polylines.lyr")

    for polyline in polylineCursor:
        cursor.insertRow([polyline[0]])
        width = findWidth(flowAccumulation, precipMap)
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
    i=1
    return i


if __name__ == '__main__':
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3])