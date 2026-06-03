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
arcpy.env.workspace = "D:/CCVA_ABM/ambR_1/scratch.gdb"
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
    
    # Do we want to apply the timestamp difference in consecutive points at this stage! 
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

    arcpy.analysis.Near(inFc1, inFc1, radius, method="GEODESIC")    # apply the "Near" to each individual bird or a feature class
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
# This is for a single bird, "tag identifier." A test case before applying for the entire birds.     
inFc2 = "USFWSLesserYellowlegs_migratory_XYTablePnt_1C_175323"

# add a new attribute as "timestamps_diff"
arcpy.AddField_management(inFc2, "timestamps_diff", "DOUBLE")

# find the timestamp difference between consecutive points
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

# Input arguments as days and convert it in hours
days = 3
days_hours = float(days * 24)    # convert days into hours, and in float or double format to compare with "timestamps_diff"

days_hours
# days_hours = 48.000

type(days_hours)

# Using .format() with AddFieldDelimiters() for smooth SQL expression execution (explained in ArcPy lecture notes)
# expression = "{0} >= {1}".format(arcpy.AddFieldDelimiters(inFc2, "timestamps_diff"), days_hours)
# order_field = "timestamp"

# Establish local variables
inFc3 = inFc2 + "_temp"
inFc2_layer = "temp_layer"

# making a feature layer from the existing feature class; the selection tool does not operate on raw feature classes on disk
arcpy.management.MakeFeatureLayer(inFc2, inFc2_layer)

# Define criteria for timestamp difference betweeen consecutive points
where_clause = f"{"timestamps_diff"} >= {days_hours}"

# Describe the object and get the OID field name
oid_field = arcpy.Describe(inFc2_layer).OIDFieldName
oid_field
len(oid_field)
type(oid_field)

# Identify the target points and get their OIDs
target_oids = []
with arcpy.da.SearchCursor(inFc2_layer, [oid_field], where_clause) as cursor:
    for row in cursor:
        target_oids.append(row[0])

target_oids
len(target_oids)
type(target_oids)

# Determine the previous OIDs 
selection_oids = []
for target_oid in target_oids:
    # Get the previous point by subtracting 1 from the OID 
    # (or adjust logic to use sequential date/time values if OIDs aren't contiguous)
    previous_oid = target_oid - 1
    
    selection_oids.extend([target_oid, previous_oid])

len(selection_oids)

# Create a comma-separated string of OIDs for the SQL query
oid_string = ", ".join(str(oid) for oid in selection_oids)
sql_expression = f"{oid_field} IN ({oid_string})"

# Select the points on the map/layer
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=inFc2_layer,
    selection_type="NEW_SELECTION",
    where_clause=sql_expression)

# Copy the selected points to a new feature class
arcpy.management.CopyFeatures(inFc2_layer, inFc3)

# --------------------------------------------------------------------------------------------------
# Applying for the whole birds by looping through the feature class based on "tag identifier"
inFc3 = "USFWSLesserYellowlegs_migratorymovements_Johnson_XYTableToPoint_1C_merged"
# inFc3 = "USFWSLesserYellowlegs_migratorymovements_Johnson_XYTableToPoint_1C"

# sort out the unique "tag_local_identifier" representing each bird
with arcpy.da.SearchCursor(inFc3, ["tag_local_identifier"]) as cursor:
    myValues1 = sorted({row[0] for row in cursor})

len(myValues1)

# Add a new attribute field for time difference between the points
arcpy.AddField_management(inFc3, "timestamps_diff", "DOUBLE")

# Calculate the time difference between the consecutive points and convert it to hours
# prev_time = None
# with arcpy.da.UpdateCursor(inFc3, [["timestamp", "timestamps_diff"]]) as cursor:
#     for row in cursor:
#         current_time = row[0]
        
#         if prev_time is not None and current_time is not None:
#             # Calculate difference in seconds 
#             delta = (current_time - prev_time).total_seconds()
#             row[1] = delta/3600       # convert it into hours
#             cursor.updateRow(row)
        
#         prev_time = current_time

# Loop through each unique bird, "tag_local_identifier"
for i in range(len(myValues1)):
    # inFc3_layer1 = inFc3_layer + "_temp_" + str(myValues[i])
    inFc3_A = inFc3 + "_temp_" + str(myValues1[i])

    where1 = "{0} = {1}".format(arcpy.AddFieldDelimiters(inFc3, "tag_local_identifier"), myValues1[i])   # use AddFieldDelimiters to avoid any issue with variables in SQL
    arcpy.management.MakeFeatureLayer(inFc3, inFc3_A, where1)  # Selection tool does not operate on the raw feature class, so a feature layer
    
    # Calculate the time difference between the consecutive points for each bird individually and convert it to hours
    prev_time = None
    with arcpy.da.UpdateCursor(inFc3_A, [["timestamp", "timestamps_diff"]]) as cursor:
        for row in cursor:
            current_time = row[0]
            
            if prev_time is not None and current_time is not None:
                # Calculate difference in seconds 
                delta = (current_time - prev_time).total_seconds()
                row[1] = delta/3600       # convert it into hours
                cursor.updateRow(row)
            
            prev_time = current_time
      
    oid_field = arcpy.Describe(inFc3_A).OIDFieldName           # Object ID using Describe

    target_oids = []
    with arcpy.da.SearchCursor(inFc3_A, [oid_field], where_clause) as cursor:   # append OIDs satisfying where_clause (>=48 hours)
        for row in cursor:
            target_oids.append(row[0])

    # check if the list is empty or not, given the days or hours criteria using where_clause. if len(target_oids) == 0 also works.
    if not target_oids:
        print("The list is empty for {0}".format(myValues1[i]))
    else:
        selection_oids = []
        for target_oid in target_oids:
            # Get the previous point by subtracting 1 from the OID 
            # (or adjust logic to use sequential date/time values if OIDs aren't contiguous)
            previous_oid = target_oid - 1

            selection_oids.extend([target_oid, previous_oid])

        oid_string = ", ".join(str(oid) for oid in selection_oids)
        sql_expression = f"{oid_field} IN ({oid_string})"

        arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=inFc3_A,
            selection_type="NEW_SELECTION",
            where_clause=sql_expression)
        
        # Copy the selected points to a new feature class
        arcpy.management.CopyFeatures(inFc3_A, inFc3_A + "_select")

    # check if the list is empty or not, given the days or hours criteria using where_clause
    # for item_oid in target_oids:
    #     if not item_oid:
    #         continue        # skip the rest of the loop block if the list is empty
    #     else:
    #         selection_oids = []
    #         for target_oid in target_oids:
    #             # Get the previous point by subtracting 1 from the OID 
    #             # (or adjust logic to use sequential date/time values if OIDs aren't contiguous)
    #             previous_oid = target_oid - 1

    #             selection_oids.extend([target_oid, previous_oid])

    #         oid_string = ", ".join(str(oid) for oid in selection_oids)
    #         sql_expression = f"{oid_field} IN ({oid_string})"

    #         arcpy.management.SelectLayerByAttribute(
    #             in_layer_or_view=inFc3_A,
    #             selection_type="NEW_SELECTION",
    #             where_clause=sql_expression)
            
    #         # Copy the selected points to a new feature class
    #         arcpy.management.CopyFeatures(inFc3_A, inFc3_A + "_select")

# Merge the all the individual bird files or feature classes 
pointList1 = []
for fc in arcpy.ListFeatureClasses("*select*"):
    pointList1.append(fc)

arcpy.management.Merge(pointList1, inFc3 + "_merged2")

# Delete the *temp* files
delList1 = arcpy.ListFeatureClasses("*select*")
for i in delList1:
    arcpy.management.Delete(i)

# Delete the *temp* files; this may not needed because *select* already deleted files with "temp" in their names
# delList2 = arcpy.ListFeatureClasses("*temp*")
# for i in delList2:
#     arcpy.management.Delete(i)

# ------------------------------------------------------------------------------------------------------------------
# select the points with "timestamps_diff" hours matching the above expression
target_id = None
with arcpy.da.SearchCursor(inFc2_layer, ["OBJECTID"], expression) as cursor:
    for row in cursor:
        target_id = row[0]

target_id

if target_id:
    # Select target and the one immediately before it
    where_clause = f"OBJECTID = {target_id} OR OBJECTID = {target_id - 1}"
    arcpy.management.SelectLayerByAttribute(inFc2_layer, "NEW_SELECTION", where_clause)


records = []
with arcpy.da.SearchCursor(inFc2_layer, ["OBJECTID", order_field, "timestamps_diff"], sql_clause=(None, f"ORDER BY {order_field}")) as cursor:
        for row in cursor:
            records.append(row)

selected_oids = []

arcpy.management.SelectLayerByAttribute(inFc2_layer, "NEW_SELECTION", expression)

with arcpy.da.SearchCursor(inFc2_layer, ["OBJECTID"], sql_clause=(None, f"ORDER BY {order_field}")) as cursor:
    for row in cursor:
        target_id = row[0]
        previous_id = target_id - 1
        
        # 3. Select current and previous point based on IDs
        select_query = f"OBJECTID = {target_id} OR OBJECTID = {previous_id}"
        arcpy.management.SelectLayerByAttribute(inFc2_layer, "NEW_SELECTION", select_query)

arcpy.management.CopyFeatures(inFc2_layer, inFc3)


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

matrix = [[1, 2], [], [3, 4]]

for sublist in matrix:
    if not sublist:
        continue  # Jumps immediately to the next sublist

    # Else execute this code
    print(f"Processing: {sublist}")


my_list = [3, 5, 6]

if not my_list:

    print("The list is empty.")
else:
    print("The list has items.")

