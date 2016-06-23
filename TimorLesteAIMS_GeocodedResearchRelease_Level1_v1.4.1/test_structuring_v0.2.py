import pandas as pd
import numpy as np
import os
from shapely.geometry import LineString, MultiPoint, mapping, shape
from scipy.spatial import Voronoi, ConvexHull
import fiona
from fiona.crs import from_epsg
import shapely.ops


dcsv = pd.read_csv('cleaned_Donors_record.csv', encoding = 'utf-8')
# get the numpy array of latitude and longitude
att_lon_lat = dcsv.loc[:, ['longitude','latitude']].values

# Adding bounding box to extend the size of voronoi result
extra_point = np.array([[5000, 5000], [5000, -5000], [-5000, -5000], [-5000, 5000]])
points_extend = np.concatenate((att_lon_lat, extra_point))

vor = Voronoi(points_extend)

#convert voronoi to line objects
lines = [
    LineString(vor.vertices[line])
    for line in vor.ridge_vertices
    # if -1 not in line
]

# get a list of polygons of voronoi tesellation
areas = list(shapely.ops.polygonize(lines))

# convert point records into multipoint
# load coordinates into multipoints object
mtpoints = MultiPoint(att_lon_lat)

# use list(points.geoms) or list(points) to access each point in MultiPoint object
list_points = list(mtpoints.geoms)

# create a schema for ESRI shapefile
outSchema = {'geometry':'Polygon', 'properties':{'donors_iso3':'str'}}
# use WGS 84 , longlat , the kind of global use of Coordinate Reference System
crs = from_epsg(4326)

# Using fiona.collection to convert polygon to shapefile
with fiona.collection('TEST2.shp','w','ESRI Shapefile', outSchema, crs) as output:
    for polygon in areas:
        attribute_each_polygon = {}
        for point in list_points:
            # use Point.within() or Polygon.contain() provided by shapely to find the point within one specific polygon
            # to see if a point within a polygon and which point it is.
            if point.within(polygon):
                is_same_lat = dcsv.latitude == point.y
                is_same_lon = dcsv.longitude == point.x
                # find the record within pandas.dataframe and copy the attribute of donors to it
                donor = str(dcsv[is_same_lat & is_same_lon].head(1).donors_iso3.values[0])
                attribute_each_polygon = {'donors_iso3': donor}
                output.write({
                    'properties': attribute_each_polygon,
                    'geometry': mapping(polygon)
                })
                break
            else:
                attribute_each_polygon = {'donors_iso3':''}

# This part below is to clip voronoi result from existing country boundary shapefile, a kind of mask.
    # this may be merged to codes above when nesessary.
bdSHP = os.getcwd()+'/TLS_adm_shp/TLS_adm0.shp'
# read country boundary shapefile
with fiona.open(bdSHP, 'r') as layer_boundary:
    with fiona.open('TEST2.shp', 'r') as layer_voronoi:
        meta_voronoi = layer_voronoi.meta
        with fiona.open('test_clipped_voronoi.shp', 'w', **meta_voronoi) as output_clip:
        # loop each polygon in boundary shapefile
            # loop every polygon in voronoi result
            attribute_each_polygon = {}
            for record_boundary in layer_boundary.filter():
                for record_polygon in layer_voronoi.filter():
                    # do intersection
                    polygon_boundary = shape(record_boundary['geometry'])
                    polygon = shape(record_polygon['geometry'])
                    intersect_polygon = polygon.intersection(polygon_boundary)

                    # attract attribute
                    attribute_donor_str =  str(record_polygon['properties']['donors_iso'])
                    attribute_each_polygon = {'donors_iso': attribute_donor_str}

                    output_clip.write({
                        'properties': attribute_each_polygon,
                        'geometry': mapping(intersect_polygon)
                    })



        # do the intersect
        # save the new polygon with the same attribute field

        # output it in shapefile.



