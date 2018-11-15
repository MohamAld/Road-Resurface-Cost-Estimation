from math import radians, cos, sin, asin, sqrt
def inBBOX(bounds, p_coords):
    '''
    :param bounds: The boundary edges of our bbox
    :param p_coords: Coordinates of the point in question, lat and long
    :return:
    '''

    plat = p_coords[0]
    plong = p_coords[1]

    if (plat >= bounds[0] and plat <= bounds[2]) and (plong >= bounds[1] and plong <= bounds[3]):
        return True
    return False




def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
                    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

