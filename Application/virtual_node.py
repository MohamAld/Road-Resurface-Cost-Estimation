'''
    This is used to find a virtual node on the boundary box if a way extends through the box.
'''
import math


def checkBoundaryIntersection(tolerance, coord, boundary):
    """
    :param tolerance: Accuracy of decimal places wanted. Enter as 0.01, etc.
    :param coord: The coordinate you wish to check [lat, lng]
    :param boundary: The boundary in BBOX format [lat1, lng1, lat2, lng2]
    :return: Boolean return if coord intersects boundary with accuracy of tolerance.
    """
    lat, lng = coord
    lat1 = boundary[0]
    lat2 = boundary[2]
    lng1 = boundary[1]
    lng2 = boundary[2]

    # Check if on Western Boundary
    if (lat > lat1) and (lat < lat2) and (abs(lng-lng1) < tolerance):
        return True

    # Check if on Eastern boundary
    if (lat > lat1) and (lat < lat2) and (abs(lng-lng2) < tolerance):
        return True

    # Check if on southern boundary
    if (lng > lng1) and (lng < lng2) and (abs(lat - lat1) < tolerance):
        return True

    # Check if on Northern boundary
    if (lng > lng1) and (lng < lng2) and (abs(lat - lat2) < tolerance):
        return True

    return False



def getPathLength(lat1,lng1,lat2,lng2):
    '''calculates the distance between two lat, long coordinate pairs'''
    R = 6371000 # radius of earth in m
    lat1rads = math.radians(lat1)
    lat2rads = math.radians(lat2)
    deltaLat = math.radians((lat2-lat1))
    deltaLng = math.radians((lng2-lng1))
    a = math.sin(deltaLat/2) * math.sin(deltaLat/2) + math.cos(lat1rads) * math.cos(lat2rads) * math.sin(deltaLng/2) * math.sin(deltaLng/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d

def getDestinationLatLong(lat,lng,azimuth,distance):
    '''returns the lat an long of destination point
    given the start lat, long, aziuth, and distance'''


    R = 6378.1 #Radius of the Earth in km
    brng = math.radians(azimuth) #Bearing is degrees converted to radians.
    d = distance/1000 #Distance m converted to km
    lat1 = math.radians(lat) #Current dd lat point converted to radians
    lon1 = math.radians(lng) #Current dd long point converted to radians

    lat2 = math.asin(math.sin(lat1) * math.cos(d/R) + math.cos(lat1)* math.sin(d/R)* math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(d/R)* math.cos(lat1), math.cos(d/R)- math.sin(lat1)* math.sin(lat2))
    #convert back to degrees
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return[lat2, lon2]

def calculateBearing(lat1,lng1,lat2,lng2):
    '''calculates the azimuth in degrees from start point to end point'''
    startLat = math.radians(lat1)
    startLong = math.radians(lng1)
    endLat = math.radians(lat2)
    endLong = math.radians(lng2)
    dLong = endLong - startLong
    dPhi = math.log(math.tan(endLat/2.0+math.pi/4.0)/math.tan(startLat/2.0+math.pi/4.0))
    if abs(dLong) > math.pi:
         if dLong > 0.0:
             dLong = -(2.0 * math.pi - dLong)
         else:
             dLong = (2.0 * math.pi + dLong)
    bearing = (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0
    return bearing


def _virtualnode(interval,azimuth,lat1,lng1,lat2,lng2, boundary):
    '''returns every coordinate pair inbetween two coordinate
    pairs given the desired interval'''

    tolerance = 0.01
    d = getPathLength(lat1, lng1, lat2, lng2)
    remainder, dist = math.modf((d / interval))
    counter = float(interval)
    coords = []
    coords.append([lat1,lng1])

    for distance in range(0,int(dist)):
        coord = getDestinationLatLong(lat1,lng1,azimuth,counter)
        counter += float(interval)
        coords.append(coord)
        if checkBoundaryIntersection(tolerance, coord, boundary):

            break
    return coords[len(coords)-1]


def virtual_node(lat1, lng1, lat2, lng2, bounds):


    interval = 1.0
    azimuth = calculateBearing(lat1,lng1,lat2,lng2)

    #print(azimuth)
    coords = _virtualnode(interval,azimuth,lat1,lng1,lat2,lng2, bounds)
    #print(coords)
    return coords



#Virtual Nodes applied: [[145.213901917185, -37.9256060285923], [0, 0]]
