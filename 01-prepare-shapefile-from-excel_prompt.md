I have an excel spreadsheet ("D:\Norm\4.13_Assessing Gulf mangrove dieback\Gulf_Aerial_Survey_2017\NESP_GOC_AerialSurveys_2017_2019.xlsx") with a sheet named 'Shoreline_Image_Database_17_19'. The attached image is a preview of the sheet. I want a Python script that will read this spreadsheet, then convert it to a shapefile saving it to '../public/Shoreline_DB/GOC_NESP-4-13_JCU_AerialSurveys_2017_2019_Shoreline_DB.shp'. I want this to only retain the columns 'Shore_FID', 'Shore_X', 'Shore_Y','2017_Image' and '2019_Image'. Before saving as a shapefile I want to join in additional attributes and add some calculated attributes. The spreadsheet also contains a sheet 'Shore_Dieback_MAP' that contains observations about each of the matching Shore_FID. I want the attributes of the 'Shore_Dieback_MAP' to be joined with the Shoreline_Image_Database_17_19. The 'Shore_Mangrove', 'Density','Type', and 'Dieback' are all integer values. The X_2017 and X_2019 are 'X' or 0 so a shore string attribute should be used. Some of the attribute names need to be shortened to fit in shapefile restructions. Image_ID_2017 -> ImgID_2017, Image_ID_2019 -> ImgID_2019, Shore_Mangrove -> Shore_Mang. I also want the following attributes calculated. 

ImageCount:
ImageCount should be the number of images available at each Shore_FID. This is based on 2017_Image and 2019_Image. If they are both NULL then ImageCount is 0, if one of them is available then ImageCount is 1 and it both are available then ImageCount is 2.

LabelScale: 
This attribute is to help with labelling the Shore_FIDs so that less labels are shown when zoomed out. Initially all rows get a starting value of 10. If the Shore_FID is a multiple of 5 then the LabelScale is changed to 9. 
Shore_FID multiple, LabelScale
1, 10
5, 9
10, 8
20, 7
50, 6
100, 5
200, 4
500, 3
1000, 2
2000, 1

This dataset corresponds to information about images and we want to organised them into groups of approximate 250 photos (or rather 250 Shore_FIDs). This is to ensure that we don't have too many photos in a folder. I want to add two attributes associated with this grouping.
The Shore_FIDs go from 1 - 19534 (this should be checked in code) these should be grouped into clusters of 250. GroupID = Shore_FID // 250 and a GroupRange = f'{GroupID*250+1}-{(min(GroupID, max(GroupID))+1)*250}', so for example:
GroupID, GroupRange
0, '1-250'
1, '251-500'
78, '19501-19534'
For the last group it should start at a multiple of 250 and end on the last Shore_FID, as shown in the example above.

The attributes should be stored efficiently and so the field lengths of the text fields should be set. 
Name, Type, length
Shore_FID, Integer 64, 10
Shore_X, Decimal double,
Shore_Y, Decimal double,
2017_Image, Text, 30
2019_Image, Text, 30
ImgID_2017, Text, 30
ImgID_2019, Text, 30
X_2017, Text, 5
X_2019, Text, 5
Shore_Mang, Integer 32, 1
Density, Integer 32, 1
Type, Integer 32, 1
Dieback, Integer 32, 1 
ImageCount, Integer 64, 10
LabelScale, Integer 64, 10

Follow ups:
Can you make sure the script generates the output directory if needed.

Can you add extensive print statements to show progress through the script, including one right at the start and one at the end.

The shapefile should have a projection file. It should have one corresponding to EPSG:4326.

There is also another shapefile in '../new-data/GOC_AIMS_Shore-drainage-divisions.shp' which is a set of polygons that cover all the shoreline points. I want to perform a spatial join to add the 'Division' and 'DivShort' attributes to the GOC_NESP-4-13_JCU_AerialSurveys_2017_2019_Shoreline_DB.shp. These attributes are text and should be 25 characters in length. Other attributes from the join should be excluded ('index_right').

Please change the output to '../public/Shoreline_DB/GOC_NESP-4-13_JCU_AerialSurveys_2017_2019_Shoreline_DB.shp'

I want to also copy the input excel spreadsheet and the 'GOC_AIMS_Shore-drainage-divisions.shp' to the output '../public/Shoreline_DB/' 

There are a bunch of rows in the original excel, where there is no Shore_X or Shore_Y. They are blank. These rows should be removed.
Also the 'LabelScale' calculation replacements were too large by 1, so needed to be adjusted. multiples.index(multiple) must be zero indexed.

Please add processing that will check if the files referred to by the Shoreline_DB are actually available on disk. If they aren't then they should be set as Null in the dataset.

The attributes '2017_Image' and '2019_Image' that correspond to the filenames of images. For example for 2017_Image: 1_2017_11_GOC_3978.JPG. Where an image is not available for a particular year then 2017_Image or 2019_Image should be considered as Null.

The path for the '2017_Image' source images is 'D:\Norm\4.13_Assessing Gulf mangrove dieback\Gulf_Aerial_Survey_2017\2017_Shoreline_Images' and the path for the '2019_Image' images is 'D:\Norm\4.13_Assessing Gulf mangrove dieback\Gulf_Aerial_Survey_2019\2019_Shoreline_Images', these correspond to surveys from the 2017 and 2019 years respectively.

The script should identify if there are any discrepancies between the predicted file names from GOC_NESP-4-13_JCU_AerialSurveys_2017_2019_Shoreline_DB and the actual images on disk. This discrepancy checking should print out progress every 500 images checked. If the image file is missing then the data should be considered as Null. This checking should be done early in the processing so if the missing files result in a Null values for both 2017 and 2019 then the whole row will be removed.

The checking has an off by one error. The very last missing image is not removed from the dataset.