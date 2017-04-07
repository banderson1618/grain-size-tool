"""

Name: Grain Size Distribution Tool
Purpose: Find the average size of gravel in a stream network

Author: Braden Anderson
Created: 31 March 2017
Last Update: 4 April 2017

"""

import arcpy
import os
from Reach import Reach


def main(dem,
         streamNetwork,
         precipMap,
         huc10,
         scratch):
    """Source code for our tool"""
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    testing = False

    if not os.path.exists(scratch+"\outputData"):
        os.makedirs(scratch+"\outputData")
    scratch += "\outputData"
    clippedStreamNetwork = scratch + "\clippedStreamNetwork.shp"
    arcpy.AddMessage("Clipping stream network...")
    arcpy.Clip_analysis(streamNetwork, huc10, clippedStreamNetwork)

    reachArray = makeReaches(testing, dem, clippedStreamNetwork, precipMap, scratch)
    for i in range(1, 2500, 100):
        arcpy.AddMessage("Slope: " + str(reachArray[i].slope))
    arcpy.AddMessage("Reach Array Created.")



def makeReaches(testing, dem, streamNetwork, precipMap, scratch):
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
    polylineCursor = arcpy.da.SearchCursor(streamNetwork, ['SHAPE@', 'SHAPE@XY'])
    arcpy.AddMessage("Calculating Drainage Area...")
    flowDirection = arcpy.sa.FlowDirection(dem)
    flowAccumulation = arcpy.sa.FlowAccumulation(flowDirection)  # Calculates the flow accumulation to use in findWidth()

    arcpy.AddMessage("Creating Reach Array...")

    """If testing, only go through the loop once. Otherwise, go through every reach"""
    if testing:
        polyline = polylineCursor.next()
        width = findWidth(flowAccumulation, precipMap, polyline[0].firstPoint)
        q_2 = findQ_2()
        slope = findSlope(dem, polyline, scratch)

        reach = Reach(width, q_2, slope, polyline[0])

        reaches.append(reach)

    else:
        for polyline in polylineCursor:
            width = findWidth(flowAccumulation, precipMap, polyline[0].firstPoint)
            q_2 = findQ_2()
            slope = findSlope(dem, polyline, scratch)

            reach = Reach(width, q_2, slope, polyline[0])

            reaches.append(reach)

    del polyline
    del polylineCursor

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

def findSlope(dem, polyline, scratch):
    """Finds the average slope of the reach in question"""
    length = polyline[0].length
    firstPointElevation = findElevationAtPoint(dem, polyline[0].firstPoint,scratch)
    secondPointElevation = findElevationAtPoint(dem, polyline[0].lastPoint, scratch)

    elevationDifference = abs(firstPointElevation - secondPointElevation)

    slope = (elevationDifference/length) * -1

    return slope


def findElevationAtPoint(dem, point, scratch):
    """Finds the elevation at a certain point based on a DEM"""
    """
    I can't find a good way to just pull the data straight from the raster, so instead, we're having to
    create the point in a layer of its own, then create another layer that has the elevation using the Extract Value
    to Points tool, then using a search cursor to get the elevation data. It's a mess, and it's inefficient, but it
    works. If anyone can find a better way, email me at banderson1618@gmail.com
    """
    sr = arcpy.Describe(dem).spatialReference
    arcpy.env.workspace = scratch
    arcpy.CreateFeatureclass_management(scratch, "point.shp", "POINT", "", "DISABLED", "DISABLED", sr)
    fc = scratch+"\point.shp"
    cursor = arcpy.da.InsertCursor(fc, ["SHAPE@"])
    cursor.insertRow([point])
    del cursor
    pointLayer = scratch+"\pointElevation"
    arcpy.sa.ExtractValuesToPoints(scratch+"\point.shp", dem, pointLayer)
    searchCursor = arcpy.da.SearchCursor(pointLayer+".shp", "RASTERVALU")
    row = searchCursor.next()
    elevation = row[0]
    del searchCursor
    del row

    return elevation


if __name__ == '__main__':
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3])