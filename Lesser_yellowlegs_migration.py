# -*- coding: utf-8 -*-

"""
Title - Selecting the multipoint feature class representing birds migration movement
"""

__author__ = "Bijan GURUNG"
__version__ = "1.0"
__email__ = "bijangurung@ksu.edu"
__status__ = "Production"

# Import required module (s)
import arcpy, os

# Set environment(s)
arcpy.env.workspace = "C:/Users/bijan/OneDrive/Desktop/CCVA_ABM/ambR_1/scratch.gdb"
arcpy.env.overwriteOutput = True

# Define local variable (s)
inFc = "USFWSLesserYellowlegs_migratorymovements_Johnson_XYTableToPoint_1C"

# get the unique values of "tag_local_identifier" (integer format) 
with arcpy.da.SearchCursor(inFc, ["tag_local_identifier"]) as cursor:
    myValues = sorted({row[0] for row in cursor})

len(myValues)

# define the search radius for "Near" geoprocessing tool
radius = "30 Kilometers"    # input parameter as the search radius
# days = 2     # input parameter as number of days 
# days_hours = days * 24   # converted to hours 

# the "Near" geoprocessing tool has to be applied individually to each bird
for i in range(len(myValues)):
    inFc1 = inFc + "_temp_" + str(myValues[i])   # local variable; myValues[i] is integer, so has to be converted to string; "temp" is also used to identify the parsed files
    where = "{0} = {1}".format(arcpy.AddFieldDelimiters(inFc, "tag_local_identifier"), myValues[i])   # use AddFieldDelimiters to avoid any issue with variables in SQL
    
    arcpy.conversion.ExportFeatures(inFc, inFc1, where)  # "Near" cannot be performed by selecting rows, so each bird has to be a seperate feature class
    
    # arcpy.AddField_management(inFc1, "timestamps_diff", "FLOAT")   # Add a new field to calculate the time difference between consecutive points
    
    # prev_time = None
    # with arcpy.da.UpdateCursor(inFc1, [["timestamp", "timestamps_diff"]]) as cursor:
    #     for row in cursor:
    #         current_time = row[0]
        
    #     if prev_time is not None and current_time is not None:
    #         # Calculate difference in seconds 
    #         delta = (current_time - prev_time).total_seconds()
    #         row[1] = delta/3600       # convert it into hours
    #         cursor.updateRow(row)
        
    #     prev_time = current_time

    # where_clause = "{0} = {1}".format(arcpy.AddFieldDelimiters(inFc1, "timestamps_diff"), days_hours)
    # with arcpy.da.UpdateCursor(inFc1, "timestamps_diff", where_clause) as cursor: 
    #     for row in cursor:
    #         if row[0] >= days_hours:
    #             cursor.deleteRow()

    arcpy.analysis.Near(inFc1, inFc1, radius, method="GEODESIC")            # apply the "Near" to each individual bird or a feature class
    with arcpy.da.UpdateCursor(inFc1, ["NEAR_FID"]) as cursor:   # "Near" feature automatically generates two features: NEAR_FID and NEAR_DIST
        for row in cursor:
            if row[0] == -1:                             # NEAR_FID == -1 are the ones that are not within the search radius of any points
                cursor.deleteRow()                       # delete the -1 value rows

# Merge the all the individual bird files or feature classes 
pointList = []
for fc in arcpy.ListFeatureClasses("*temp*"):
    pointList.append(fc)

arcpy.management.Merge(pointList, inFc + "_merged")

# Delete the *temp* files
delList = arcpy.ListFeatureClasses("*temp*")
for i in delList:
    arcpy.management.Delete(i)
    
# ----------------------------------------------------------------------------------------------------------------------------------------------
    
inFc2 = "USFWSLesserYellowlegs_migratory_XYTablePnt_1C_175323"

prev_time = None

with arcpy.da.UpdateCursor(inFc2, [["timestamp", "timestamps_diff"]]) as cursor:
    for row in cursor:
        current_time = row[0]
        
        if prev_time is not None and current_time is not None:
            # Calculate difference in seconds 
            delta = (current_time - prev_time).total_seconds()
            row[1] = delta/3600       # convert it into hours
            cursor.updateRow(row)
        
        prev_time = current_time

86280/3600

days = 2
days_hours = days * 24

expression = "{0} >= {1}".format(arcpy.AddFieldDelimiters(inFc2, "timestamps_diff"), days_hours)

arcpy.management.SelectLayerByAttribute(inFc2, "NEW_SELECTION", expression)

with arcpy.da.SearchCursor(inFc2, ["OBJECTID"]) as cursor:
    for row in cursor:
        target_id = row[0]
        previous_id = target_id - 1
        
        # 3. Select current and previous point based on IDs
        select_query = f"OBJECTID = {target_id} OR OBJECTID = {previous_id}"
        arcpy.management.SelectLayerByAttribute(inFc2, "NEW_SELECTION", select_query)





# for i in range(len(myValues)):
#     where = '"tag_local_identifier" = ' + "'" + myValues[i] + "'"
#     arcpy.conversion.ExportFeatures(outFc, outFc + "_"+ myValues[i], where)

# where = '"tag_local_identifier" = ' + "'" + str(175323) + "'"
# where = '"tag_local_identifier" = 175323'
# radius = "30 Kilometers"

# where = '"visible" = "true"'

# target_id = 175323
# field_name = "tag_local_identifier"

# where_clause = '"tag_local_identifier" = ' + "'" + str(target_id) + "'"

# where_clause = "{0} = {1}".format(arcpy.AddFieldDelimiters(inFc, field_name), target_id)

# where_clause = arcpy.AddFieldDelimiters(inFc, field_name) + " = " + str(target_id)

# with arcpy.da.SearchCursor(inFc, "tag_local_identifier", where_clause) as cursor:
#     for row in cursor:
#         print(f"Found record with {field_name}: {row[0]}")

# with arcpy.da.SearchCursor(inFc, "tag_local_identifier", where) as cursor:
#     for row in cursor:
#         arcpy.analysis.Near(inFc, inFc, radius, method="GEODESIC")

# with arcpy.da.SearchCursor(inFc, "visible", where) as cursor:
#     for row in cursor:
#         arcpy.analysis.Near(inFc, inFc, radius)

# fields = arcpy.ListFields(inFc)
# print(f"Fields in {os.path.basename(inFc)}:")
# for field in fields:
#     print(f"  Name: {field.name:<20} Type: {field.type:<15} Length: {field.length}")

