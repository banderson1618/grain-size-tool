import arcpy
import GrainSize


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GrainSize"
        self.alias = "Grain Size Distribution"

        # List of tool classes associated with this toolbox
        self.tools = [GrainSizeTool]


class GrainSizeTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Grain Size Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName = "DEM",
            name = "DEM",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Input",
            multiValue=False)

        param1 = arcpy.Parameter(
            displayName = "Stream Network",
            name = "streamNetwork",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Input",
            multiValue=False)

        param2 = arcpy.Parameter(
            displayName = "Precipitation",
            name = "precipMap",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Input",
            multiValue=False)

        param3 = arcpy.Parameter(
            displayName = "HUC 10 Boundary",
            name = "huc10",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Input",
            multiValue=False)

        param4 = arcpy.Parameter(
            displayName = "Output Files Folder",
            name = "scratchWorkspace",
            datatype = "DEFolder",
            parameterType = "Required",
            direction = "Input",
            multiValue=False)

        params = [param0, param1, param2, param3, param4]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        GrainSize.main(parameters[0].valueAsText,
         parameters[1].valueAsText,
         parameters[2].valueAsText,
         parameters[3].valueAsText,
         parameters[4].valueAsText)
        return
