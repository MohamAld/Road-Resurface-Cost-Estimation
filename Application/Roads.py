from virtual_node import virtual_node
from useful_functions import inBBOX, haversine


class Road:

    def __init__(self, name, tag, nodes, bounds_array, lanes):
        self.name = name
        self.tag = tag
        self.lanes = lanes
        self.nodes = nodes
        self.area = 0
        self.bounds = bounds_array
        self.first_outside = False
        self.second_outside = False
        # print(self.name + " Lanes: " + self.lanes)
        #print(self.nodes)
        self.fix_nodes()

    def fix_nodes(self):
        '''
        This will only remove nodes from our array if they lie outside the boundary.
        Only the node closet to boundary is kept; but is then removed in order to
        Create a virtual node as replacement for it, which is at the intersection of boundary
        with the way.
        :return: modified self.nodes
        '''

        first_maintained_node = False
        second_maintained_node = False
        first_part = False

        '''Loop through until we find intersection with the boundary for this way.'''
        for i in range(len(self.nodes)):
            current_node = self.nodes[i]
            lat = current_node.lat
            lon = current_node.lon
            if not (inBBOX(self.bounds, [lat, lon])):

                if not first_part:
                    if not first_maintained_node:
                        first_maintained_node = current_node
                        self.first_outside = True

                    else:

                        self.nodes[i - 1] = 0
                        first_maintained_node = current_node
                else:
                    if not second_maintained_node:
                        second_maintained_node = current_node
                        self.second_outside = True
                    else:
                        self.nodes[i] = 0
            else:
                first_part = True
                continue
        #print(self.nodes)

        #Clean self.nodes from all zero entires now
        while 0 in self.nodes:
            self.nodes.remove(0)
        #print("Cleaned: " + str(self.nodes))

        if not len(self.nodes) or len(self.nodes) == 1:
           # print("ALL NODES OUTSIDE! ! ! ! ! ! ! ! ! ! ! ! ! ! !")
            return


        if first_maintained_node:
            self.nodes[0] = virtual_node(self.nodes[0].lat, self.nodes[0].lon, self.nodes[1].lat, self.nodes[1].lon, self.bounds)
        if second_maintained_node:
            self.nodes[len(self.nodes)-1] = virtual_node(self.nodes[len(self.nodes)-2].lat, self.nodes[len(self.nodes)-2].lon, self.nodes[len(self.nodes)-1].lat, self.nodes[len(self.nodes)-1].lon, self.bounds)

        if not first_maintained_node:
            self.nodes[0] = [float(self.nodes[0].lat), float(self.nodes[0].lon)]
        if not second_maintained_node:
            node = self.nodes[len(self.nodes)-1]
            self.nodes[len(self.nodes)-1] = [float(node.lat), float(node.lon)]
        for i in range(1, len(self.nodes)-1):
            # print(self.nodes[i])
            self.nodes[i] = [float(self.nodes[i].lat), float(self.nodes[i].lon)]
            # print(self.nodes[i])
        # Final loop through to remove potential [0, 0] nodes.
        for i in range(len(self.nodes)):
            if self.nodes[i] == [0, 0]:
                del self.nodes[i]
                i -= 1
                if i < 0:
                    i = 0
                if i > len(self.nodes)-1:
                    break



        self.calc_area()

        # print("Virtual Nodes applied: " + str(self.nodes))

        # print("Area " + str(self.area))



    def estimate_width(self):

        """
        Classify road using extracted parameters
        Get number of lanes if possible, multiply to get width
        :return: width(m)
        """
        multi = 1 # The Number of Lanes
        lane_width = 3.5
        padding = 0.9
        if self.lanes != "n/a":
            multi = int(self.lanes)
        tag = self.tag
        if tag in ["motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "service","road"]:
            return (multi * lane_width) + padding
        else:
            return lane_width



    def calc_area(self):
        """
        This is only called after the nodes are pre-processed by fixNodes()
        The haversine distance between each pair of nodes is calculated, then multiplied by an area
        based on the road's estimated width (infer from classification)

        :return: area in m^2
        """

        # Go through the nodes and haversine the dstance
        width = self.estimate_width()
        i = 0
        self.area = 0
        while i < len(self.nodes)-1:
            # get distance from node i to node i+1
            # multiply by width and add to total area
            # area is returned in m^2
            length = haversine(self.nodes[i][0], self.nodes[i][1], self.nodes[i+1][0], self.nodes[i+1][1]) * 1000
            self.area += length * width
            i += 1

