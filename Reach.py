class Reach(object):
    def __init__(self, width, q_2, polyline, xyPosition):
        """

        :type length: length of the given polyline
        :type xyPosition: The x y position of the centroid of the polyline
        :type width: The average width of the reach
        :type q_2: The flow at a 2 year flood
        :type polyline: The complete polyline
        """
        self.length = polyline.length
        self.xyPosition = xyPosition
        self.width = width
        self.q_2 = q_2
        self.polyline = polyline
