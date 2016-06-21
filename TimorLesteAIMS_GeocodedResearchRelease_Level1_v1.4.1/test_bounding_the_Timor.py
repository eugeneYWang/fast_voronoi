import pandas as pd
import numpy as np
import os
from shapely.geometry import LineString, MultiPoint, mapping
from scipy.spatial import Voronoi, ConvexHull
import fiona
from fiona.crs import from_epsg
import shapely.ops


dcsv = pd.read_csv('cleaned_Donors_record.csv', encoding = 'utf-8')
att_lon_lat = dcsv.loc[:, ['longitude','latitude']].values



# outSchema = {'geometry':'Point', 'properties':{'donors_iso3':'str'}}
# # use WGS 84 , longlat , the kind of global use of Coordinate Reference System
# crs = from_epsg(4326)
#
# list_out_bound_vertices = []
# # get vertices of point outside bounded polygon
# for p# oint in list_vertices:
#     if point.within(union_areas):
#         continue
#     else:
#         list_out_bound_vertices.append([point.x, point.y])
#
# conv = ConvexHull(list_out_bound_vertices)
#
# # use outbounded points to do contex hull analysis
# conv = ConvexHull(list_out_bound_vertices)
# conv_lines = [
#     LineString(conv.points[index])
#     for index in conv.neighbors
# ]
#
# # lines.extend(conv_lines)
#
# # get a list of polygons of voronoi tesellation
# # areas = list(shapely.ops.polygonize(lines))
# areas = list(shapely.ops.polygonize(conv_lines))
#


# output them in shapefile
# create a schema for ESRI shapefile
outSchema = {'geometry':'Polygon', 'properties':{'donors_iso3':'str'}}
# use WGS 84 , longlat , the kind of global use of Coordinate Reference System
crs = from_epsg(4326)

# alternative : append some points with ( 5000, 5000) and other three corners
extra_point = np.array([[5000, 5000], [5000, -5000], [-5000, -5000], [-5000, 5000]])
att_lon_lat = np.concatenate((att_lon_lat, extra_point))


vor = Voronoi(att_lon_lat)

lines = [
    LineString(vor.vertices[line])
    for line in vor.ridge_vertices
    #if -1 not in line
]

areas = list(shapely.ops.polygonize(lines))

with fiona.collection('test_bounding_the_Timor2.shp', 'w', 'ESRI Shapefile', outSchema, crs) as output:
    for polygon in areas:
        attribute_each_polygon = {'donors_iso3': ''}
        output.write({
            'properties': attribute_each_polygon,
            'geometry': mapping(polygon)}
        )