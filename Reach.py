class Reach(object):
    def __init__(self, width, q_2, slope, polyline):
        """
        :type width: The average width of the reach
        :type q_2: The flow at a 2 year flood
        :type slope: The average slope of the reach
        :type polyline: The complete polyline
        :type xyPosition: The x y position of the centroid of the polyline
        """
        self.width = width
        self.q_2 = q_2
        self.slope = slope
        self.polyline = polyline

        self.grainSize = -1
        self.t_c = -1
        self.flowAccumulation = -1

    def calculateGrainSize(self, n, t_c):
        self.grainSize = (n**.6) * (self.q_2**.6) * (self.width**-.6) * (self.slope ** .7)
        self.grainSize /= t_c
        self.grainSize /= 1.65
        self.grainSize *= 1000 # converts to millimeters

    def calculateT_c(self, n):
        self.t_c = (n**.6) * (self.q_2**.6) * (self.width**-.6) * (self.slope ** .7)
        self.t_c /= 1.65
        self.t_c *= 1000
        self.t_c /= self.grainSize

    def setFlowAccumulation(self, flowAccumulation):
        self.flowAccumulation = flowAccumulation

    def setGrainSize(self, grainSize):
        self.grainSize = grainSize