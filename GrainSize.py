########################################################################################################################
# Name: Grain Size Distribution Tool                                                                                   #
# Purpose: Find the average size of gravel in a stream network. Because the Q_2 value is localized, this will not work #
# outside the Columbia River Basin, though modifying findQ_2() for a particular region should be relatively simple.    #
#                                                                                                                      #
# Author: Braden Anderson                                                                                              #
# Created: 31 March 2017                                                                                               #
# Last Update: 10 April 2017                                                                                           #
########################################################################################################################

import arcpy
import os
from Reach import Reach


def main(dem,
         streamNetwork,
         precipMap,
         huc10,
         scratch,
         nValue,
         t_cValue,
         regionNumber):
    """Source code for our tool"""
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    testing = True

    """Creates the output file, where we'll stash all our results"""
    if not os.path.exists(scratch+"\outputData"):
        os.makedirs(scratch+"\outputData")
    scratch += "\outputData"

    """Clips our stream network to a HUC10 region"""
    clippedStreamNetwork = scratch + "\clippedStreamNetwork.shp"
    arcpy.AddMessage("Clipping stream network...")
    arcpy.Clip_analysis(streamNetwork, huc10, clippedStreamNetwork)\

    """Makes the reaches"""
    reachArray = makeReaches(testing, dem, clippedStreamNetwork, precipMap, regionNumber, scratch, nValue, t_cValue)

    """Outputs data. Delete in final build"""
    if testing:
        for reach in reachArray:
            arcpy.AddMessage("Width: " + str(reach.width) + " meters")
            arcpy.AddMessage("Q_2: " + str(reach.q_2) + " cubic feet per second")
            arcpy.AddMessage("Slope: " + str(reach.slope))
            arcpy.AddMessage("Grain Size: " + str(reach.grainSize) + " ")
            arcpy.AddMessage(" ")
    else:
        for i in range(1, 2500, 100):
            arcpy.AddMessage("Width: " + str(reachArray[i].width))
            arcpy.AddMessage("Q_2: " + str(reachArray[i].q_2))
            arcpy.AddMessage("Slope: " + str(reachArray[i].slope))
            arcpy.AddMessage("Grain Size: " + str(reachArray[i].grainSize))
            arcpy.AddMessage(" ")

    """Calculates the grain size for the reaches"""
    #if not testing:  #not yet, just a reminder that this needs to happen eventually
        #for reach in reachArray:
            #reach.calculateGrainSize(nValue, t_cValue)


def makeReaches(testing, dem, streamNetwork, precipMap, regionNumber, scratch, nValue, t_cValue):
    """Goes through every reach in the stream network, calculates its width and Q_2 value, and stores that data in a
    Reach object, which is then placed in an array"""

    reaches = []
    polylineCursor = arcpy.da.SearchCursor(streamNetwork, ['SHAPE@'])
    arcpy.AddMessage("Calculating Drainage Area...")
    flowDirection = arcpy.sa.FlowDirection(dem)
    flowAccumulation = arcpy.sa.FlowAccumulation(flowDirection)  # Calculates the flow accumulation to use in findWidth()
    cellSizeX = arcpy.GetRasterProperties_management(flowAccumulation, "CELLSIZEX")
    cellSizeY = arcpy.GetRasterProperties_management(flowAccumulation, "CELLSIZEY")
    cellSize = float(cellSizeX.getOutput(0)) * float(cellSizeY.getOutput(0))
    numReachesString = str(arcpy.GetCount_management(streamNetwork))

    arcpy.AddMessage("Creating Reach Array...")

    """If testing, only go through the loop once. Otherwise, go through every reach"""
    if testing:
        for i in range(10):
            for j in range(10):
                polyline = polylineCursor.next()

            slope = findSlope(dem, polyline, scratch)
            width = findWidth(flowAccumulation, precipMap, scratch, cellSize)
            q_2 = findQ_2(flowAccumulation, precipMap, scratch, cellSize, regionNumber)

            reach = Reach(width, q_2, slope, polyline[0])
            reach.calculateGrainSize(nValue, t_cValue)

            reaches.append(reach)

    else:
        i = 0
        for polyline in polylineCursor:

            slope = findSlope(dem, polyline, scratch)
            width = findWidth(flowAccumulation, precipMap, scratch, cellSize)
            q_2 = findQ_2(flowAccumulation, precipMap, scratch, cellSize, regionNumber)

            reach = Reach(width, q_2, slope, polyline[0])
            reach.calculateGrainSize(nValue, t_cValue)

            reaches.append(reach)
            i += 1
            arcpy.AddMessage("Completed Reach " + str(i) + " out of " + numReachesString)


    del polyline
    del polylineCursor

    arcpy.AddMessage("Reach Array Created.")

    return reaches


def findQ_2(flowAccumulation, precipMap, scratch, cellSize, regionNumber):
    """Returns the value of a two year flood event"""
    #TODO: Write findQ_2()
    searchCursor = arcpy.da.SearchCursor(scratch + "\precipPoint.shp", "Inches")
    row = searchCursor.next()
    precip = row[0]
    del row, searchCursor

    searchCursor = arcpy.da.SearchCursor(scratch + "\\flowPoint.shp", "RASTERVALU")
    row = searchCursor.next()
    flowAccAtPoint = row[0]
    flowAccAtPoint *= cellSize # multiplies by the size of the cell to get area
    flowAccAtPoint /= 2589988 # converts to square miles, which our formula requires
    if flowAccAtPoint < 0:
        flowAccAtPoint = 0

    if regionNumber == 1:
        q_2 = 0.35 * (flowAccAtPoint**0.923) * (precip ** 1.24)
    elif regionNumber == 2:
        q_2 = 0.09 * (flowAccAtPoint**0.877) * (precip ** 1.51)
    elif regionNumber == 3:
        q_2 = 0.817 * (flowAccAtPoint**0.877) * (precip ** 1.02)
    elif regionNumber == 4:
        q_2 = 0.025 * (flowAccAtPoint**0.880) * (precip ** 1.70)
    elif regionNumber == 5:
        q_2 = 14.7 * (flowAccAtPoint**0.815)
    elif regionNumber == 6:
        q_2 = 2.24 * (flowAccAtPoint**0.719) * (precip ** 0.833)
    elif regionNumber == 7:
        q_2 = 8.77 * (flowAccAtPoint**0.629)
    elif regionNumber == 8:
        q_2 = 12.0 * (flowAccAtPoint**0.761)
    else:
        q_2 = 0.803 * (flowAccAtPoint**0.672) * (precip ** 1.16)

    return q_2


"""NOTE: To improve efficiency, this function is using a point file created in findSlope(). If findSlope() isn't
executed in front of findWidth(), or if it no longer needs to create a point, this function will break."""
def findWidth(flowAccumulation, precipMap, scratch, cellSize):
    """Estimates the width of a reach, based on its drainage area and precipitation levels"""
    pointLayer = scratch + "\point.shp"
    arcpy.Intersect_analysis([pointLayer, precipMap], "precipPoint")
    searchCursor = arcpy.da.SearchCursor(scratch + "\precipPoint.shp", "Inches")
    row = searchCursor.next()
    precip = row[0]
    precip *=2.54 # converts to centimeters
    del row, searchCursor

    arcpy.sa.ExtractValuesToPoints(scratch+"\point.shp", flowAccumulation, scratch + "\\flowPoint")
    searchCursor = arcpy.da.SearchCursor(scratch + "\\flowPoint.shp", "RASTERVALU")
    row = searchCursor.next()
    flowAccAtPoint = row[0]
    flowAccAtPoint *= cellSize
    flowAccAtPoint /= 1000000 # converts from square meters to square kilometers
    if flowAccAtPoint < 0:
        flowAccAtPoint = 0

    del row, searchCursor

    width = 0.177 * (flowAccAtPoint ** 0.397) * (precip ** 0.453)
    return width


def findSlope(dem, polyline, scratch):
    """Finds the average slope of the reach in question"""
    length = polyline[0].length
    firstPointElevation = findElevationAtPoint(dem, polyline[0].firstPoint,scratch)
    secondPointElevation = findElevationAtPoint(dem, polyline[0].lastPoint, scratch)

    elevationDifference = abs(firstPointElevation - secondPointElevation)

    slope = elevationDifference/length

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