# import modules
import pandas as pd
import numpy as np
import os

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
listCol = ['latitude', 'longitude', 'donors_iso3']

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
print ('information has been aggregated to' + CSVfile_name)

import shapely.geometry
from scipy.spatial import Voronoi

# get the numpy array of latitude and longitude
arr_lat_lon = cleaned_data[:, ['latitude', 'longitude']].values

#Voronoi
vor = Voronoi(arr_lat_lon)

#convert it to line objects
lines = [
    shapely.geometry.LineString(vor.vertices[line])
    for line in vor.ridge_vertice
    if -1 not in line
]

import fiona
import shapely.ops

areas = list(shapely.ops.polygonize(lines))

# pseudo code :
# Using fiona.collection to convert polygon to shapefile
# when assigning attribute to polygon
# use select by location services provided by shapely to find the point within one specific polygon
# find copy the attribute of donors to it.
# finish the process of conversion of polygon.
