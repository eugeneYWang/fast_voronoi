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

# function 2: writetoCSV(outputCSV, lat_comparing,lon_comparing,donor_ISO3_list)
# purpose: to write several attribute into a record in a CSV file.
# input: outputCSV -- the CSV file object of output file , lat_comparing -- the latitude, lon_comparing -- the longitude,
        # donor_ISO3_list -- the donor attribute
# output(return): nothing
# output file: CSV containing latitude, longitude, donor_ISO3
def writetoCSV(outputCSV, lat_comparing, lon_comparing, donor_ISO3_list):
    outputStr = '\"'+lat_comparing+'\",\"'+ lon_comparing+'\",\"'
    strDonor = ""
    i = 0
    for str in donor_ISO3_list:
        if i != 0:
            strDonor += "|"
        strDonor += str
        i += 1
    outputStr += strDonor + '\"'
    outputCSV.write(outputStr)



# read csv | 1. Pandas used here
address = os.getcwd()
oldCSV = pd.read_csv(address+'//data//level_1a.csv')

outputCSVname = 'cleaned_Donors_record.csv'
outputCSV = open(outputCSV,'w')

print oldCSV
print 'the type of oldCSV is %s' %(type(oldCSV))
print oldCSV[1: 1], oldCSV[0: 0]
print type(oldCSV.columns), type(oldCSV.index)
print oldCSV.get_value(0, 0, True)
print type(oldCSV.get_value(0, 0, True))
print oldCSV.shape

# clean duplicate records
# start
row_number, col_number = oldCSV.shape # get count of rows and columns
comparing_record_index = 0
# get the list of index of records we need to check, from 1 to the end
list_check = []
list_check.extend(range(1, row_number))
# initial the list of donors
donor_ISO3_list = []
donor_ISO3_list = str(oldCSV.get_value(comparing_record_index, 'donors_iso3')).split('|')
while len(list_check) > 0:
    # Pick the first record as example, record its x and Y
    lat_comparing = oldCSV.get_value(comparing_record_index, 'latitude')
    lon_comparing = oldCSV.get_value(comparing_record_index, 'longitude')
    # initial a list of records that still need to look at.
    list_restcheck = []
    # loop the rest to see if XY is the same
    for i in list_check:
        # if they are same to the original XY,
        if (oldCSV.get_value(i, 'latitude') == lat_comparing & oldCSV.get_value(i, 'longitude') == lon_comparing):
            temp_donorlist = str(oldCSV.get_value(i, 'donor_iso3')).split('|')
            donor_ISO3_list = combineTwoList(donor_ISO3_list, temp_donorlist)
            # record the donor into a new list
            # or record more things
        # if they are not same
        else:
            # record this index to list "The rest"so that "the rest"to be search onother time
            list_restcheck.append(i)
    writetoCSV(outputCSV, lat_comparing,lon_comparing,donor_ISO3_list)

    #list_check = list_restcheck
    comparing_record_index = list_restcheck[0]
    # check the length of list "The rest" equals 1,
    if len(list_restcheck) == 1:  # if it is one, write this record to CSV
        lat_comparing = oldCSV.get_value(comparing_record_index, 'latitude')
        lon_comparing = oldCSV.get_value(comparing_record_index, 'longitude')
        temp_donorlist = str(oldCSV.get_value(i, 'donor_iso3')).split('|')
        donor_ISO3_list = combineTwoList(donor_ISO3_list, temp_donorlist)
        writetoCSV(outputCSV, lat_comparing, lon_comparing, donor_ISO3_list)
        break
    list_check = list_restcheck[1:]
oldCSV.close()



            # if yes : go back to looping again to check the rest and its spatially overlaping records.
            # if not: Swich: 1(record this), 0(break the loop)

    # output the result as CSV file


# put those overlapsed records into one record, and their donors

# output a new CSV file

# 2. GIS-related Library

# finish the cluster analysis (Or other methods) to separate points

# do voronoi analysis as many times as the number of clusters






