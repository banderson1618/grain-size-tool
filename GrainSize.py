########################################################################################################################
# Name: Grain Size Distribution Tool
# Purpose: Find the average size of gravel in a stream network. Because the Q_2 value is localized, this will not work
# outside the Columbia River Basin, though modifying findQ_2() for a particular region should be relatively simple.
#
# Author: Braden Anderson
# Created: 31 March 2017
# Last Update: 18 May 2017
########################################################################################################################

import arcpy
import os
from Reach import Reach
from math import sqrt


def main(dem,               # Path to the DEM file
         streamNetwork,     # Path to the stream network file
         precipMap,         # Path to the precipitation map file
         huc10,             # Path to the polygon of our HUC10 region
         outputFolder,      # Path to where we want to store our output
         nValue,            # Our Manning coefficient
         t_cValue,          # Our torque value
         regionNumber):     # Which region we use for our Q2 equation
    """Source code for our tool"""
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")  # We'll be using a bunch of spatial analysis tools

    testing = False  # Runs a limited case if we don't want to spend hours of our life watching a progress bar
    if testing:
        arcpy.AddMessage("TESTING")

    """Creates the temporary data folder, where we'll put all our intermediate results"""
    if not os.path.exists(outputFolder+"\\temporaryData"):
        os.makedirs(outputFolder+"\\temporaryData")
    tempData = outputFolder + "\\temporaryData"

    """Creates our output folder, where we'll put our final results"""
    if not os.path.exists(outputFolder+"\outputData"):
        os.makedirs(outputFolder+"\outputData")
    outputDataPath = outputFolder+"\outputData"

    """Clips our stream network to a HUC10 region"""
    if huc10 != None:
        clippedStreamNetwork = tempData + "\clippedStreamNetwork.shp"
        arcpy.AddMessage("Clipping stream network...")
        arcpy.Clip_analysis(streamNetwork, huc10, clippedStreamNetwork)
    else:
        clippedStreamNetwork = streamNetwork

    """Makes the reaches"""
    reachArray = makeReaches(testing, dem, clippedStreamNetwork, precipMap, regionNumber, tempData, nValue, t_cValue)

    """Writes our output to a folder"""
    writeOutput(reachArray, outputDataPath)

    """Writes data to a text file. Delete in final build"""
    writeResults(reachArray, testing, outputDataPath)


def makeReaches(testing, dem, streamNetwork, precipMap, regionNumber, tempData, nValue, t_cValue):
    """Goes through every reach in the stream network, calculates its width and Q_2 value, and stores that data in a
    Reach object, which is then placed in an array"""

    reaches = []
    numReaches = int(arcpy.GetCount_management(streamNetwork).getOutput(0))
    numReachesString = str(numReaches)
    arcpy.AddMessage("Reaches to calculate: " + numReachesString)
    printEstimatedTime(numReaches)

    polylineCursor = arcpy.da.SearchCursor(streamNetwork, ['SHAPE@'])
    arcpy.AddMessage("Calculating Drainage Area...")
    dem = arcpy.sa.Fill(dem)
    flowDirection = arcpy.sa.FlowDirection(dem)
    flowAccumulation = arcpy.sa.FlowAccumulation(flowDirection)  # Calculates the flow accumulation to use in findWidth()
    cellSizeX = arcpy.GetRasterProperties_management(flowAccumulation, "CELLSIZEX")
    cellSizeY = arcpy.GetRasterProperties_management(flowAccumulation, "CELLSIZEY")
    cellSize = float(cellSizeX.getOutput(0)) * float(cellSizeY.getOutput(0))
    arcpy.SetProgressor("step", "Creating Reach 1 out of " + numReachesString, 0, numReaches, 1)

    arcpy.AddMessage("Creating Reach Array...")

    """If testing, only go through the loop once. Otherwise, go through every reach"""
    if testing:
        for i in range(10):
            arcpy.AddMessage("Creating Reach " + str(i+1) + "out of 10")
            row = polylineCursor.next()
            arcpy.AddMessage("Calculating Slope...")
            lastPointElevation = findElevationAtPoint(dem, row[0].lastPoint, tempData)
            firstPointElevation = findElevationAtPoint(dem, row[0].firstPoint, tempData)
            arcpy.AddMessage("Calculating Flow Accumulation...")
            flowAccAtPoint = findFlowAccumulation(flowAccumulation, tempData, cellSize)
            arcpy.AddMessage("Calculating Precipitation...")
            precip = findPrecipitation(precipMap, tempData)

            arcpy.AddMessage("Finding Variables...")
            slope = findSlope(row, firstPointElevation, lastPointElevation)
            width = findWidth(flowAccAtPoint, precip)
            q_2 = findQ_2(flowAccAtPoint, precip, regionNumber)

            reach = Reach(width, q_2, slope, row[0])
            reach.calculateGrainSize(nValue, t_cValue)

            reaches.append(reach)
            arcpy.AddMessage("Reach " + str(i+1) + " complete.")
    else:
        i = 0
        for row in polylineCursor:
            lastPointElevation = findElevationAtPoint(dem, row[0].lastPoint, tempData)
            firstPointElevation = findElevationAtPoint(dem, row[0].firstPoint, tempData)
            flowAccAtPoint = findFlowAccumulation(flowAccumulation, tempData, cellSize)
            precip = findPrecipitation(precipMap, tempData)

            slope = findSlope(row, firstPointElevation, lastPointElevation)
            width = findWidth(flowAccAtPoint, precip)
            q_2 = findQ_2(flowAccAtPoint, precip, regionNumber)

            reach = Reach(width, q_2, slope, row[0])
            reach.calculateGrainSize(nValue, t_cValue)

            reaches.append(reach)
            i += 1
            arcpy.AddMessage("Creating Reach " + str(i) + " out of " + numReachesString + " (" +
                             str((float(i)/float(numReaches))*100) + "% complete)")

    del row
    del polylineCursor

    arcpy.AddMessage("Reach Array Created.")

    return reaches


def findQ_2(flowAccAtPoint, precip, regionNumber):
    """Returns the value of a two year flood event"""
    """These equations are based on the USGS database. To find your region, go to the following website:
    https://pubs.usgs.gov/fs/fs-016-01/ """
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
    elif regionNumber == 9:
        q_2 = 0.803 * (flowAccAtPoint**0.672) * (precip ** 1.16)
    elif regionNumber == 10:
        q_2 = 0.334 * (flowAccAtPoint**0.963)
    else:
        arcpy.AddError("Incorrect Q_2 value entered")

    q_2 /= 35.3147  # converts from cubic feet to cubic meters

    return q_2


def findWidth(flowAccAtPoint, precip):
    """Estimates the width of a reach, based on its drainage area and precipitation levels"""
    width = 0.177 * (flowAccAtPoint ** 0.397) * (precip ** 0.453)  # This is the equation we're using to estimate width
    if width < .3:  # establishes a minimum width value
        width = .3
    return width


def findSlope(polyline,firstPointElevation, secondPointElevation):
    """Finds the average slope of the reach in question"""
    length = polyline[0].length
    elevationDifference = abs(firstPointElevation - secondPointElevation)
    slope = elevationDifference/length
    return slope


def findFlowAccumulation(flowAccumulation, tempData, cellSize):
    """Because our stream network doesn't line up perfectly with our flow accumulation map, we need to create a
         buffer and search in that buffer for the max flow accumulation using Zonal Statistics"""
    arcpy.Buffer_analysis(tempData + "\point.shp", tempData + "\pointBuffer.shp", "20 Meters")
    arcpy.PolygonToRaster_conversion(tempData + "\pointBuffer.shp", "FID", tempData + "\pointBufferRaster.tif",
                                     cellsize=sqrt(cellSize))
    maxFlow = arcpy.sa.ZonalStatistics(tempData + "\pointBufferRaster.tif", "Value", flowAccumulation, "MAXIMUM")
    arcpy.sa.ExtractValuesToPoints(tempData + "\point.shp", maxFlow, tempData + "\\flowPoint")

    searchCursor = arcpy.da.SearchCursor(tempData + "\\flowPoint.shp", "RASTERVALU")
    row = searchCursor.next()
    flowAccAtPoint = row[0]
    del row
    del searchCursor
    flowAccAtPoint *= cellSize  # gives us the total area of flow accumulation, rather than just the number of cells
    flowAccAtPoint /= 1000000  # converts from square meters to square kilometers
    if flowAccAtPoint < 0:
        flowAccAtPoint = 0

    return flowAccAtPoint


def findPrecipitation(precipMap, tempData):
    pointLayer = tempData + "\point.shp"
    arcpy.Intersect_analysis([pointLayer, precipMap], "precipPoint")
    searchCursor = arcpy.da.SearchCursor(tempData + "\precipPoint.shp", "Inches")
    row = searchCursor.next()
    precip = row[0]
    precip *= 2.54  # converts to centimeters
    del row, searchCursor
    return precip


def findElevationAtPoint(dem, point, tempData):
    """Finds the elevation at a certain point based on a DEM"""
    """
    I can't find a good way to just pull the data straight from the raster, so instead, we're having to
    create the point in a layer of its own, then create another layer that has the elevation using the Extract Value
    to Points tool, then using a search cursor to get the elevation data. It's a mess, and it's inefficient, but it
    works. If anyone can find a better way, email me at banderson1618@gmail.com
    """
    sr = arcpy.Describe(dem).spatialReference
    arcpy.env.workspace = tempData
    arcpy.CreateFeatureclass_management(tempData, "point.shp", "POINT", "", "DISABLED", "DISABLED", sr)
    cursor = arcpy.da.InsertCursor(tempData+"\point.shp", ["SHAPE@"])
    cursor.insertRow([point])
    del cursor
    pointLayer = tempData+"\pointElevation"
    arcpy.sa.ExtractValuesToPoints(tempData+"\point.shp", dem, pointLayer)
    searchCursor = arcpy.da.SearchCursor(pointLayer+".shp", "RASTERVALU")
    row = searchCursor.next()
    elevation = row[0]
    del searchCursor
    del row

    return elevation


def writeResults(reachArray, testing, outputData):
    """This function is meant to save the results for future study"""
    testOutput = open(outputData + "\Data(readable).txt", "w")
    i = 0
    for reach in reachArray:
        i += 1
        testOutput.write("Reach " + str(i) + ":")
        testOutput.write("\nWidth: " + str(reach.width) + " meters")
        testOutput.write("\nQ_2: " + str(reach.q_2) + " cubic meters per second")
        testOutput.write("\nSlope: " + str(reach.slope))
        testOutput.write("\nGrain Size: " + str(reach.grainSize) + "\n\n")
    testOutput.close()

    inputDataFile = open(outputData + "Data(for_reach_construction).txt", "w")
    for reach in reachArray:
        inputDataFile.write("\n" + str(reach.width))
        inputDataFile.write("\n" + str(reach.q_2))
        inputDataFile.write("\n" + str(reach.slope))
        inputDataFile.write("\n" + str(reach.grainSize))
    inputDataFile.close()


def writeOutput(reachArray, outputDataPath):
    arcpy.env.workspace = outputDataPath
    outputShape = outputDataPath + "\GrainSize.shp"
    tempLayer = outputDataPath + "\GrainSize_lyr"
    outputLayer = outputDataPath + "\GrainSize.lyr"
    arcpy.CreateFeatureclass_management(outputDataPath, "GrainSize.shp", "POLYLINE", "", "DISABLED", "DISABLED")
    arcpy.AddField_management(outputShape, "GrainSize", "DOUBLE")

    insertCursor = arcpy.da.InsertCursor(outputShape, ["SHAPE@", "GrainSize"])
    for reach in reachArray:
        insertCursor.insertRow([reach.polyline, reach.grainSize])
    del insertCursor

    sr = arcpy.SpatialReference("NAD 1983 UTM Zone 11N")
    arcpy.DefineProjection_management(outputShape, sr)

    arcpy.MakeFeatureLayer_management(outputShape, tempLayer)
    arcpy.SaveToLayerFile_management(tempLayer, outputLayer)


def printEstimatedTime(numReaches):
    totalSeconds = numReaches * 11
    numHours = totalSeconds / 3600
    numMinutes = (totalSeconds / 60) % 60
    arcpy.AddMessage("Estimated time to complete: " + str(numHours) + " Hours, " + str(numMinutes) + " Minutes")


if __name__ == '__main__':
    main(os.sys.argv[1],
         os.sys.argv[2],
         os.sys.argv[3])