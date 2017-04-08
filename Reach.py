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

    self.grainSize = -1

    def calculateGrainSize(self, n, t_c):
        self.grainSize = 1.65 * (n**.6) * (q_2**.6) * (w**-.6) * (slope ** .7)
        self.grainSize = self.grainSize / t_c
