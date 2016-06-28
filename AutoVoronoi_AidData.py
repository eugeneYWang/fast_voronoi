"""
Author: Eugene Wang
This code can be found in this Github Address: https://github.com/eugeneYWang/fast_voronoi
Established at Jun 23 2016
"""
import pandas as pd
import numpy as np
import os
from shapely.geometry import LineString, MultiPoint, mapping, shape
from scipy.spatial import Voronoi, ConvexHull
import fiona
from fiona.crs import from_epsg
import shapely.ops

'''
# function 1: aggregate_lv1_by_location()
# description: Aggregate records from level1 by location
# input: input_df ( input dataframe containing level1 data), setting_csv_address = 'default' ( a csv file only showing
    which fields should be included), filter_field (To choose a specific field to filter the file), filter_value
    (the specific value wanted from filter_field)
# return:cleaned_df(cleaned dataframe)
'''
def aggregate_lv1_by_location(input_df, setting_csv_address = 'default', filter_dict = None):


    # read setting file to get a list of fields needed.
    if setting_csv_address == 'default':
        list_fields = read_setting('default_setting_voronoi.csv')
    else:
        try:
            list_fields = read_setting(setting_csv_address)
        except:
            print 'The setting file has an incorrect address or incorrect format'

    # filter the dataframe with filter_dict
    filtered_subset = filter_dataframe(input_df, filter_dict)

    # get dataframe with only the fields listed in the setting file
    list

    comparing_index = 0
    count_total = len(filtered_subset)
    # when there is still records in dataframe
    while len(filtered_subset) >0:
        # get the latitude and longitude to compare with others
        lat_comparing = filtered_subset.head(1).latitude[comparing_index]
        lon_comparing = filtered_subset.head(1).longitude[comparing_index]
        is_nan_lat = str(lat_comparing) == 'nan'
        is_nan_lon = str(lon_comparing) == 'nan'

        # to judge if the position is the same with comparing record
        is_lat = input_df.latitude == lat_comparing
        is_lon = input_df.longitude == lon_comparing

        # exclude records with position of NaN
        if (is_nan_lat | is_nan_lon):
            input_df = input_df[is_lat | is_lon]
            if len(input_df) == 0:
                break
            comparing_index = input_df.head(1).index[0]
            count_now = len(input_df)
            print "progress : %s / %s" % (count_now, count_total)
            continue

        # get dataframe of overlaping points
        subset_overlapping = filtered_subset[is_lat & is_lon]

        # set_ISO3 = set(subset_overlapping.donors_iso3.tolist())
        str_donor = ''



    return


'''
function 1.1: read_setting()
description: load setting csv into dataframe
input: csv(Setting CSV address or 'default')
return: dataframe (dataframe of setting)
'''
def read_setting(csv):
    dataframe = pd.read_csv(csv, encoding='utf-8')
    return dataframe

'''
function 1.2: filter_dataframe()
description: filter dataframe based on certain conditions in filter_dict
input: subset_overlapping(a dataframe), filter_dict(a dictionary, key is field name and values are conditions)
return: filtered_subset

sample of filter_dict:
{'sector': [311,310,998], 'donor': ['USA','ESP']}
'''
def filter_dataframe(subset_overlapping, filter_dict):
    list_keys = subset_overlapping.keys()
    list_values = subset_overlapping.values()
    condition = None
    condition_all = None

    # loop every key and value to complete boolean value
    for i in range(len(list_keys)):
        # if a couple keywords are searching as words in one key (eg. searching 311, 310, 998 from sector)
        for itemkey in list_keys:
            if type(list_values[i]) is list:
                # if a list as a value, use logical OR to combine all boolean
                for ii in list_values[i]:
                    if condition is None:
                        is_condition = subset_overlapping[i] == ii
                        condition = is_condition
                    else:
                        is_condition = subset_overlapping[i] == ii
                        condition = condition | is_condition

                # use logical AND to combine boolean to boolean of other values
                if condition_all is None:
                    condition_all = condition
                else:
                    condition_all = condition_all & condition
                condition = None
            # if only one word or value is searched ( 'donor' = 'USA', for example)
            elif len(list_values[i]) == 1:
                if condition_all is None:
                    condition_all = subset_overlapping[i] == list_values[i]
                else:
                    is_condition = subset_overlapping[i] == list_values[i]
                    condition_all = condition_all & is_condition
            elif len(list_values[i]) == 0:
                continue

    # dataframe that satisfy all conditions
    filtered_subset = subset_overlapping[condition_all]
    if len(filtered_subset) == 0:
        print 'No such a record is found.'
        quit()

    return filtered_subset


'''
function 2: polygonize_list()
# description:
# input: vor(Scipy.Voronoi() object )
# return: list_polygon [if times allow, planning to make my own class including polygon and its attributes]
'''
def polygonize_list(vor):

    return

'''
# function 3: output_clipped_voronoi()
# desciption: clip voronoi polygon by mask of country, spatially join fields to polygons.
# input:cleaned_df, list_polygon
# return: none
# output: ESRI shapefile
'''
def output_clipped_voronoi(cleaned_df, list_polygon):

    return


'''
# function 4:
# desciption: based on aggregated dataframe, output voronoi analysis in shapefile and fields as attribute
# input:
# return:
'''

#####################################################################################################################
'''
This function is executed only when this script will be run directly.
'''
def main():
    # read level1 csv data
    dcsv = pd.read_csv(os.getcwd()+'TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1//Data//level_1a.csv')
    clean_df = aggregate_lv1_by_location(dcsv)

# do voronoi analysis

# get list of polygon, with spatially joined data

# clip polygon with certain mask

# output dataframe in polygon




if __name__ ==  '__main__':
    main()