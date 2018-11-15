from virtual_node import virtual_node
from useful_functions import inBBOX, haversine


class vRoad:
    def __init__(self, name, nodes, bounds_array, width, dir):
        self.name = name
        self.nodes = nodes[0]
        self.bounds = bounds_array
        self.first_outside = False
        self.second_outside = False
        self.width = width
        self.area = 0
        #print(dir)
        #print(self.name)
        self.Process()

    def Process(self):
        '''
        This will only remove nodes from our array if they lie outside the boundary.
        Only the node closet to boundary is kept; but is then removed in order to
        Create a virtual node as replacement for it, which is at the intersection of boundary
        with the way.
        It advances on to the next stage, calculating the area for the road per node pair.
        '''

        first_maintained_node = False
        second_maintained_node = False
        first_part = False

        '''Loop through until we find intersection with the boundary for this way.'''
        for i in range(len(self.nodes)):
            current_node = self.nodes[i]
            lat = current_node[1]
            lon = current_node[0]
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

        # Clean self.nodes from all zero entires now
        while 0 in self.nodes:
            self.nodes.remove(0)

        if not len(self.nodes) or len(self.nodes) == 1:
            #print("ALL NODES OUTSIDE! ! ! ! ! ! ! ! ! ! ! ! ! ! !")
            return

        if first_maintained_node:
            arr = virtual_node(self.nodes[0][1],
                               self.nodes[0][0],
                               self.nodes[1][1],
                               self.nodes[1][0],
                               self.bounds)
            # print("APPLIED : " + str(arr))

            self.nodes[0] = [arr[1], arr[0]]
        if second_maintained_node:
            arr = virtual_node(self.nodes[len(self.nodes) - 2][1],
                               self.nodes[len(self.nodes) - 2][0],
                               self.nodes[len(self.nodes) - 1][1],
                               self.nodes[len(self.nodes) - 1][0],
                               self.bounds)
            self.nodes[len(self.nodes) - 1] = [arr[1], arr[0]]



        self.area_calculation()
        #print(self.area)

    def area_calculation(self):
        '''
        Calculates the area per the nodes of the way and the seal width extracted.
        :return: AREA in m2
        '''

        # Loop through our nodes. Do each pair together.
        i = 0
        self.area = 0
        total_length = 0

        while i < len(self.nodes)-1:
            # get distance from node i to node i+1
            # multiply by width and add to total area
            # area is returned in m^2
            total_length += haversine(self.nodes[i][1], self.nodes[i][0], self.nodes[i+1][1], self.nodes[i+1][0]) * 1000
            i += 1
        #print("Length: " + str(total_length) + "Width: " + str(self.width))
        self.area = total_length * self.width
        #print("Area: " + str(self.area))
