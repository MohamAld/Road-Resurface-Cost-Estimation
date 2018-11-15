import overpy
import numpy as np
import json
import urllib.request
from Roads import Road
from vRoads import vRoad
import math
api = overpy.Overpass()


def find_index(arr, name):

    for i in range(len(arr)):
        if arr[i] == name:
            return i
    return -1

def queryVicRoads(bounds):
    #Build URL
    url = "https://services2.arcgis.com/18ajPSI0b3ppsmMt/arcgis/rest/services/Road_Width_and_Number_of_Lanes/FeatureServer/0/query?where=1%3D1&outFields=*&geometry="
    bounds_query = str(bounds[1]) + "%2C" + str(bounds[0]) + "%2C" + str(bounds[3]) + "%2C" + str(bounds[2])
    request_url = url + bounds_query + "&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outSR=4326&f=json"


    with urllib.request.urlopen(request_url) as response:
        res = response.read()
    response = json.loads(res.decode('utf-8'))


    return response


def convertnsew(array):
    '''
    array format: lat1, long1, lat2, long2
    '''
    #Extract the lat and long of each, and then convert to Overpass-friendly query bounds.
    swl = array[0]
    swlo = array[1]
    nel = array[2]
    nelo = array[3]

    lat1 = min(max(swl, -90), 90)
    lat2 = min(max(nel, -90), 90)
    lng1 = min(max(swlo, -180), 180)
    lng2 = min(max(nelo, -180), 180)



    return [lat1, lng1, lat2, lng2]


def process(bounds_string):
    '''
    :param bounds_string: string of bounds to be converted for usage in api.query
    :return: query results for processing
    '''
    bound_array = bounds_string.split(", ")

    bound_array = np.asfarray(bound_array, float)

    bounds_array = convertnsew(bound_array)

    # initalize an array with names to skip.

    queried_roads = []

    # Query with Vicroads first, extract relevant streets.

    response = queryVicRoads(bounds_array)
    validLetters = "abcdefghijklmnopqrstuvwxyz"

    area_road = []
    name_road = []


    vnodes = []
    onodes = []

    for i in range(len(response['features'])):

        #Extract the data, pass each segment into a class which handles its area calculations for us
        information = response['features'][i]
        v_Road = vRoad(information['attributes']['ROAD_NAME'], information['geometry']['paths'], bounds_array, information['attributes']['SEAL_WIDTH'], information['attributes']['DIRECTION'])
        name = v_Road.name.lower()

        filtered_name = ''.join([char for char in name if char in validLetters]).replace("hwy", "").replace("highway", "").replace("fwy", "").replace("freeway", "").replace("rd", "").replace("road", "")

        queried_roads.append(filtered_name)

        index = find_index(name_road, v_Road.name)

        if index != -1:
            area_road[index] += v_Road.area

        else:
            area_road.append(v_Road.area)
            name_road.append(v_Road.name)

        vnodes.append(v_Road.nodes)
        # Add a comparable version of the name.

    query = "way("+str(bounds_array[0])+","+str(bounds_array[1])+","+str(bounds_array[2])+","+str(bounds_array[3])+") [\"highway\"];" + """
    (._;>;);
    out body;
    """
    result = api.query(query)

    for way in result.ways:

        # print("Name: %s" % way.tags.get("name", "n/a"))
        # print("  Highway: %s" % way.tags.get("highway", "n/a"))
        # print("  Nodes:")
        # for node in way.nodes:
        #     print("    Lat: %f, Lon: %f" % (node.lat, node.lon))
        name = way.tags.get("name","n/a").lower()

        filtered_name = ''.join([char for char in name if char in validLetters]).replace("hwy", "").replace("highway","").replace("fwy", "").replace("freeway", "").replace("rd", "").replace("road", "")

        if not (filtered_name in queried_roads):
            myRoad = Road(way.tags.get("name", "n/a"), way.tags.get("highway", "n/a"), way.nodes, bounds_array, way.tags.get("lanes", "n/a"))

            index = find_index(name_road, myRoad.name)

            if index != -1:
                area_road[index] += myRoad.area

            else:
                area_road.append(myRoad.area)
                name_road.append(myRoad.name)
            onodes.append(myRoad.nodes)

    #
    # output_text = ''
    # for i in range(len(name_road)):
    #     if name_road[i] == 'n/a':
    #         continue
    #     output_text += '\n' + str(name_road[i]) + ' Area: ' + str(area_road[i]) + ' km^2'
    # output_text += '\nTotal Area:' + str(sum(area_road)) + ' km^2'

    #output.mapbbox.setText(output_text)


    return [name_road, area_road]

