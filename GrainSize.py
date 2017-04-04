"""

Name: Grain Size Distribution Tool
Purpose: Find the average size of gravel in a stream network

Author: Braden Anderson
Created: 31 March 2017
Last Update: 4 April 2017

"""

import arcpy
from Reach import Reach

def main(dem,
         streamNetwork,
         precipMap,
         projection):
    """Source code for our tool"""
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    """Testing where the coordinates of the DEM are. Will delete later"""
    demBottom = arcpy.GetRasterProperties_management(dem, "BOTTOM")
    demLeft = arcpy.GetRasterProperties_management(dem, "LEFT")
    demTop = arcpy.GetRasterProperties_management(dem, "TOP")
    demRight = arcpy.GetRasterProperties_management(dem, "RIGHT")
    arcpy.AddMessage(demBottom.getOutput(0))
    arcpy.AddMessage(demLeft.getOutput(0))
    arcpy.AddMessage(demTop.getOutput(0))
    arcpy.AddMessage(demRight.getOutput(0))

    desc = arcpy.Describe(streamNetwork)
    reachArray = makeReaches(dem, streamNetwork, precipMap, desc.spatialReference)
    arcpy.AddMessage("Reach Array Created.")

    for i in range(10):
        arcpy.AddMessage(str(reachArray[i].xyPosition))

    q_2 = findQ_2()


def makeReaches(dem, streamNetwork, precipMap, projection):
    """Creates a series of reaches """
    # TODO: Fix the reach's xy coordinates being wrong
    """This commented out code was used to make sure that the layer's data itself wasn't being messed up
    when it entered the program. I'm keeping it around because we'll probably have to save something as a layer
    eventually anyways"""
    # arcpy.env.workspace = "C:\Users\A02150284\Documents\ArcGIS\TestMapData"
    # arcpy.MakeFeatureLayer_management("NHD_Asotin_all_segmeneted.shp", "polylines_lyr")
    # arcpy.SaveToLayerFile_management("polylines_lyr", "C:\Users\A02150284\Documents\ArcGIS\TestMapData\polylines.lyr")

    """Goes through every reach in the stream network, calculates its width and Q_2 value, and stores that data in a
    Reach object, which is then placed in an array"""
    reaches = []
    polylineCursor = arcpy.da.SearchCursor(streamNetwork, ['SHAPE@', 'SHAPE@XY'], "", projection)
    arcpy.AddMessage("Calculating Drainage Area...")
    flowDirection = arcpy.sa.FlowDirection(dem)
    flowAccumulation = arcpy.sa.FlowAccumulation(flowDirection)  # Calculates the flow accumulation to use in findWidth()

    arcpy.AddMessage("Creating Reach Array...")
    for polyline in polylineCursor:
        width = findWidth(flowAccumulation, precipMap, polyline[0].firstPoint)
        q_2 = findQ_2()
        reach = Reach(width, q_2, polyline[0], polyline[1])

        reaches.append(reach)

    return reaches


def findQ_2():
    """Returns the value of a two year flood event"""
    #TODO: Write findQ_2()
    i = 1  # placeholder
    return i


def findWidth(dem, precipMap, point):
    """Estimates the width of a reach, based on its drainage area and precipitation levels"""
    #TODO: Write findWidth()
    i = 1  # placeholder
    return i


if __name__ == '__main__':
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3])