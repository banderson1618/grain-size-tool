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
        self.xyPosition = polyline.centroid

    grainSize = -1

    def calculateGrainSize(self, n, t_c):
        if self.width == 0:
            self.grainSize = 0
        else:
            self.grainSize = 1.65 * (n**.6) * (self.q_2**.6) * (self.width**-.6) * (self.slope ** .7)
            self.grainSize = self.grainSize / t_c
