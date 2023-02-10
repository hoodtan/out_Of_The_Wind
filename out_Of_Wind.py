######################
## Out of the wind###
######################

# Purpose: To easily identify which direction each part of the coast faces. From this we can surmize which wind direction blows offshore, i.e. is sheltered. 
# Programmer: J.A.
# Date: February 9, 2023

# Import required libraries 
import os
import shutil
import arcpy 


#This code is useful for NS Elevation Explorer data. Extract all zipped folders to a new folder using 7Zip then run this code.
def find_tif_files(folder_path):
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.tif'):
                source = os.path.join(subdir, file)
                destination = os.path.join(folder_path, file)
                shutil.move(source, destination)

find_tif_files('') # location of unzipped tif files
print('Successfully extracted tif files from folder')


################
## A R C P Y ###
################

# variables to use to make the script more easily editable 
import arcpy
cell_Size = 5
buffer_Value = 100 


# creating a new geodatabase to store our outputs. 
# this is optional, you can just comment out the code and point to the path to your gdb if preferred. 

folder_path = 'C:\\temp\\'
gdb_path ='file.gdb'
print('creating gdb...')
arcpy.CreateFileGDB_management(folder_path, gdb_path)
print('gdb created...')


arcpy.env.workspace = '' # the location where your downloaded and unzipped DEMs are stored
tif_files = arcpy.ListRasters("*.tif")
print(f'the tif files in the specified workspace are : {tif_files}')


# creating the mosaic                       # tif files, workspace, output, coordinate system, pixel depth, cell size, band number, mosaic operators
mosaic = arcpy.MosaicToNewRaster_management(tif_files, "C:\\temp\\file.gdb", 'mosaic.tif', "", "16_BIT_SIGNED", cell_Size, "1", "LAST", "FIRST")
print(f'mosaiced {mosaic}')


# have to set our workspace to the gdb to continue the analysis 
arcpy.env.workspace = folder_path + gdb_path
print('set the workspace the the geodatabase')

# tidying the mosaic. Usually there is a no data value of -1 post mosaic, so we get rid of that using extract by attributes.

tidy_mosaic = arcpy.sa.ExtractByAttributes('tif', "VALUE <> -1");tidy_mosaic.save(folder_path+gdb_path+ '//tidy_mosaic')
print(f'tidy mosaic dataset created...')

 # deriving contour from the mosaic DEM
contours = arcpy.sa.Contour(tidy_mosaic, "intermediate_Contours",  5, 0, 1, "CONTOUR", None ) # create contour inputs 
print(f'creating intermediate contour layer...')

# selecting only 0m contours
contour_selection = arcpy.management.SelectLayerByAttribute(contours, "NEW_SELECTION", "Contour = 0", None)
print(f'selecting only 0m contour...')

# writing the selection to a new feature class 
arcpy.management.CopyFeatures( contour_selection, "zerom_Contour")
print(f'copying selection to new feature layer...')

# delete full contour layer 
arcpy.Delete_management(contours)
print(f'deleting the intermediate contour layer...')

# buffering from 0m contour
buffer = arcpy.analysis.Buffer("zerom_Contour", "buffered", buffer_Value,  "FULL", "ROUND", "ALL", "", "PLANAR" )
print(f'creating a {buffer_Value} buffer from the 0m contour')


# extract by mask
extract = arcpy.sa.ExtractByMask(tidy_mosaic, buffer, 'INSIDE')
extract.save(folder_path+gdb_path+ '//extract')
print(f'extracting portion of the DEM using the {buffer} layer as a mask')

# aspect 
aspect = arcpy.sa.Aspect(extract, 'PLANAR','METER', '');aspect.save(folder_path+gdb_path+'//aspect_Script')
print('created the aspect map')

print('done')