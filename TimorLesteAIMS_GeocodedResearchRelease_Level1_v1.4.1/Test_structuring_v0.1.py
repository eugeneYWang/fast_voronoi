# import modules
import pandas as pd
import numpy as np
import os
from shapely.geometry import LineString, MultiPoint, mapping
from scipy.spatial import Voronoi
import fiona
from fiona.crs import from_epsg
import shapely.ops

# function 1: combineTwolist(l1,l2)
# purpose: to combine all elements in the latter list into the first list while no same element will be added.
# input: l1 -- the list to have new elements added, l2 -- the list to contribute elements
# output: list -- the new-element-added list
def combineTwoList(l1, l2):
    if len(l1) == 0:
        l1 = l2
        return l1
    else:
        for str in l2:
            if str in l1:
                continue
            else:
                l1.append(str)
                continue
    return l1
# --------------------------------------------------------

# read csv | 1. Pandas used here
address = os.getcwd()
oldCSV = pd.read_csv(address+'//data//level_1a.csv')

# set up the list of column title
# listCol = ['latitude', 'longitude', 'donors_iso3']

# since repeatly use pandas.append() to add a row is a performance hit
# As suggested, I will insert row content as a dictionary to a list
list_rows = []

comparing_index = 0
count_total = len(oldCSV)

while len(oldCSV) > 0:
    # get the latitude and longitude to compare with others
    lat_comparing = oldCSV.head(1).latitude[comparing_index]
    lon_comparing = oldCSV.head(1).longitude[comparing_index]
    is_nan_lat = str(lat_comparing) == 'nan'
    is_nan_lon = str(lon_comparing) == 'nan'

    is_lat = oldCSV.latitude == lat_comparing
    is_lon = oldCSV.longitude == lon_comparing

    # if lat or lon is NaN, jump to next loop and continue comparing
    # if the rest records are all NaN on lat and lon, break the loop
    if (is_nan_lat | is_nan_lon):
        oldCSV = oldCSV[is_lat | is_lon]
        if len(oldCSV) == 0:
            break
        comparing_index = oldCSV.head(1).index[0]
        count_now = len(oldCSV)
        print "progress : %s / %s" % (count_now, count_total)
        continue

    # get dataframe of overlaping points
    subset_overlapping = oldCSV[is_lat & is_lon]
    set_ISO3 = set(subset_overlapping.donors_iso3.tolist())
    str_donor = ''

    # get a list of unique values of ISO3 code
    list_donor = []
    for e in set_ISO3:
        temp_list_donor = str(e).split('|')
        list_donor = combineTwoList(list_donor, temp_list_donor)
    list_donor.sort()

    # put those unique elements into a string
    ii = 0
    for strItem in list_donor:
        if ii != 0:
            str_donor += "|"
        str_donor += strItem
        ii += 1

    # a row of records on one position
    list_temp = {'latitude':lat_comparing,'longitude':lon_comparing,'donors_iso3':str_donor}
    list_rows.append(list_temp)
    # next loop will check the rest of records not checked yet
    oldCSV = oldCSV[~(is_lat & is_lon)]
    # have a new index to compare with the rest records.
    comparing_index = oldCSV.head(1).index[0]
    count_now = len(oldCSV)
    print "progress : %s / %s" %(count_now, count_total)

# create the dataframe with all rows of information about positions
cleaned_data = pd.DataFrame(list_rows)
CSVfile_name = 'cleaned_Donors_record.csv'
cleaned_data.to_csv(CSVfile_name, encoding='utf-8')
print ('information has been aggregated to ' + CSVfile_name)

# get the numpy array of latitude and longitude
arr_lat_lon = cleaned_data.loc[:, ['longitude', 'latitude']].values

#Voronoi
vor = Voronoi(arr_lat_lon)

#convert it to line objects
lines = [
    LineString(vor.vertices[line])
    for line in vor.ridge_vertices
    if -1 not in line
]

# lines = [
#     LineString(vor.vertices[line])
#     for line in vor.ridge_vertices
# ]

# lines = []
# for line in vor.ridge_vertices:
#     if -1 not in line:
#         lines.append(LineString(vor.vertices[line]))

# get vertices points outside those bounded polygons
# make a contex hull analysis
# append line strings of contex hull to lines list.
# do the polygonize again with the new linestring

# get a list of polygons of voronoi tesellation
areas = list(shapely.ops.polygonize(lines))

# pseudo code :

# These codes below try to assign attribute to polygon

# convert point records into multipoint
# load coordinates into multipoints object
mtpoints = MultiPoint(arr_lat_lon)

# use list(points.geoms) or list(points) to access each point in MultiPoint object
list_points = list(mtpoints.geoms)

# create a schema for ESRI shapefile
outSchema = {'geometry':'Polygon', 'properties':{'donors_iso3':'str'}}
# use WGS 84 , longlat , the kind of global use of Coordinate Reference System
crs = from_epsg(4326)

# to extend schema in the future, add this:
# outSchema['properties']['a field name you want'] = 'the type of field values shoule be'
# since  outSchema['propertiies'] is essentially a dictionary

# Using fiona.collection to convert polygon to shapefile
with fiona.collection('TEST1.shp','w','ESRI Shapefile', outSchema,crs) as output:
    for polygon in areas:
        attribute_each_polygon = {}
        for point in list_points:
            # use Point.within() or Polygon.contain() provided by shapely to find the point within one specific polygon
            # to see if a point within a polygon and which point it is.
            if point.within(polygon):
                is_same_lat = cleaned_data.latitude == point.y
                is_same_lon = cleaned_data.longitude == point.x
                # find the record within pandas.dataframe and copy the attribute of donors to it
                donor = str(cleaned_data[is_same_lat & is_same_lon].head(1).donors_iso3.values[0])
                attribute_each_polygon = {'donors_iso3': donor}
                output.write({
                    'properties': attribute_each_polygon,
                    'geometry': mapping(polygon)
                })
                break
            else:
                attribute_each_polygon = {'donors_iso3':''}



            # do the things below

    # find a way to update the schema of
# finish the process of conversion of polygon.
