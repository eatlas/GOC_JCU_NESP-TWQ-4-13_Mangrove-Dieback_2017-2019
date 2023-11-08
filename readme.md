# Gulf of Carpentaria Mangrove Dieback Shoreline imagery 2017 - 2019 (NESP TWQ 4.13, JCU)
Eric Lawrey - 6 Nov 2023
This document records the transformation of the original source project data into a form suitable for web delivery. This transformation includes:
- Converting the Shoreline Database from a spreadsheet to a shapefile. Joining in shore line dieback assessment into the table of images. 
- Adjusting the names of the attributes to fit with limitations of shapefiles.
- Downsampling and recompressing the original imagery to shrink the image data from the original 310 GB down to 40 GB. The resolution reduction (6 M pixel images) and compression levels (85% JPEG quality) were chosen carefully so that nearly all the useable information is retained in the compressed version of the data. This compression makes it much more feasible to share the dataset, and makes browsing and using the imagery much faster. Note: The original source imagery will be available on request.
- Splitting the images into regional sub-directories. To limit the number of images in each directory and to allow users to download only regions that they care about we split the data into 6 sections along the coast. For this we split them based on river catchment divisions used in the project report.


## Data Dictionary:

### GOC_NESP-4-13_JCU_AerialSurveys_2017_2019_Shoreline_DB.shp
In the following list of attributes the first name corresponds to the name in the original data (NESP_GOC_AerialSurveys_2017_2019.xlsx) and the name in the shapefile.

- **Shore_FID:** Shore_FID. Identifier of the segment along the shoreline transect. This is a continuous counter from 1 (North West of Gulf of Carpentaria) to 19534 (Western side of Cape York). Each segment is space approxiately 100 m apart. Images in the survey are aligned to the closest transect segment. This allows the repeat surveys over multiple years to be compared.
- **Image_ID_2017:** ImgID_2017. Name of the original 2017 aerial photograph, prior to adding the Shore_FID to the image filename.
- **Image_ID_2019:** ImgID_2019. Name of the original 2019 aerial photograph, prior to adding the Shore_FID to the image filename.
- **X_2017:** X_2017. ??
- **X_2019:** X_2019. ??
- **Shore_Mangrove:** Shore_Mang. 
- **Density:** Density.
- **Type:** Type.
- **Dieback:** Dieback.
- **ImageCount:** Number of survey images in each transect segment. 0 - No survey imagery, 1 - One image from either 2017 or 2019, 2 - images from both 2017 and 2019.
- **Division:** Division of the shoreline into sections correspond to major river catchments. The Division attribute is the human readable version of the division name.
- **DivShort:** Short version of the division name. This is used for the directories that the images are stored in. Having the images split into these regions limits the number of images per directory and allows users to download a division subsection of the imagery. 
    - **Division (DivShort)**
    - Roper (Roper)
    - South-West Gulf (SW-Gulf)
    - Flinders-Leichhardt (FL-group)
    - South-East Gulf (SE-Gulf)
    - Mitchell (Mitchell)
    - Western Cape (W-Cape)


## Processing:
This section documents the transformation from the original data to the version used for the web mapping and the downsampled compressed version of the imagery.

### Tools:
- QGIS: This was used for shapefile preparation.
- Python: This was used for downsampling and compressing the imagery, and filing them in the DivShort directories.

### Processing steps:
1. The original `NESP_GOC_AerialSurveys_2017_2019.xlsx / Shoreline_Image_Database_17_19` was exported as a CSV (`NESP_GOC_AerialSurveys_2017_2019_Shoreline_DB.csv`).
2. The `NESP_GOC_AerialSurveys_2017_2019.xlsx / Shore_Dieback_MAP` was exported as a CSV (`NESP_GOC_AerialSurveys_2017_2019_Shore_Dieback.csv`).
3. This CSV was then loaded into Excel to shortern the attribute names to be compatible with shapefiles. 
- **Original attribute: Shapefile attribute**
- Shore_FID: Shore_FID
- Image_ID_2017: ImgID_2017
- Image_ID_2019: ImgID_2019
- X_2017: X_2017
- X_2019: X_2019
- Shore_Mangrove: Shore_Mang
- Density: Density
- Type: Type
- Dieback: Dieback
4. In QGIS this CSV (`NESP_GOC_AerialSurveys_2017_2019_Shore_Dieback.csv`) was then loaded and a join performed with `NESP_GOC_AerialSurveys_2017_2019_Shoreline_DB.csv` based on the Shore_FID.
5. This was then exported as `NESP_GOC_AerialSurveys_2017_2019_Shoreline_DB.shp`
6. To split the data into difference regions we imported the `Australian River Basins 1997 (GA)` [dataset](https://eatlas.org.au/data/uuid/ea0a81fd-c864-4035-b51a-e214fa0a57b4) from the eAtlas into QGIS. This was used to divide the data into the following regions:
- Roper (Roper)
- South-West Gulf (SW-Gulf)
- Flinders-Leichhardt (FL-group)
- South-East Gulf (SE-Gulf)
- Mitchell (Mitchell)
- Western Cape (W-Cape)
Using Figure 2.1 from Duke et al. (2020) as a guide. The short names are intended for file paths and so need to be short and were inspired by Figure 1.4.

7. In the next couple of steps we take the transect locations (points), convert it into a line segment, buffer it to make a polygon (a long narrow polygon along the coast), then cut this up into the divisions. We then use this, with a spatial join, to assign the divisions back to the original transect locations.
`Vector creation > Points to path`
Input layer: NESP_GOC_AerialSurveys_2017_2019_Shoreline_DB
Order expression: Shore_FID
Paths: (Create temporary layer)
8. `Vector > Geoprocessing tools > Buffer`
Input layer: Paths
Distance: 0.05 degrees

9. We then enabled editing on this feature and used the `Split Features` editing tool to cut the buffered line into segments matching the river boundaries.

10. Attributes were added to record the division name:
Name: Divison
Type: Text
Length: 20

Name: DivShort
Type: Text
Length: 15

![](media/preview-divisions.jpg)

This was then saved as `GOC_AIMS_Shore-drainage-divisions.shp`.

11. Now perform a spatial join to add the division path information to the locations.
`Vector > Data Management Tools > Join Attributes by Location..`
Base Layer: NESP_GOC_AerialSurveys_2017_2019_Shoreline_DB
Join layer: GOC_AIMS_Shore-drainage-divisions
Geometric predicate: intersects

This was then saved to `Shoreline_DB\\NESP_GOC_AerialSurveys_2017_2019_Shoreline_DB.shp`

The `DivShort` attribute is used by the script (`01_prepare_images.py`) that processes the imagery to know which directory to file the imagery into.

12. Create an attribute that is the number of images in each segment.
Use the Field Calculator:
```
CASE 
  WHEN "2017_Image" IS NULL AND "2019_Image" IS NULL THEN 0
  WHEN "2017_Image" IS NULL OR "2019_Image" IS NULL THEN 1
  ELSE 2
END
```

13. Clean up the attributes by deleting the `Folder_201`, `Folder_2_1`, `begin` and `end` attributes that are no longer relevant and resave the shapefile.

14. Create a simplified version of GOC_AIMS_Shore-drainage-divisions for the metadata page.
`Vector > Geometry Tools > Simplify`
Input layer: GOC_AIMS_Shore-drainage-divisions
Tolerance: 0.02
Simplified: (Create temporary layer)

`Vector > Geoprocessing Tools > Dissolve`
Input layers: Simplified
Dissolve: (Create temporary layer)

`Right click > Export > Save Features As ...`
Format: GeoJSON
Filename: derived\\Shoreline_DB\\GOC_NESP-4-13_JCU_AerialSurveys_Study-area.geojson
Layer Options, COODINATE_PRECISION: 5

## 01_prepare_images.py GPT-4 Prompt:
I have two folders with thousands of JPEG files (most are 24 M pixel images), corresponding to surveys in 2017 and 2019. I want a Python script to down sample the images to a maximum size of 3000x2000 pixels (width x height) and a compression level that will result in images being approximately 1.5 MB (I can tune the compression quality through testing). The images are stored in the folder: F:\Norm\4.13_Assessing Gulf mangrove dieback\Gulf_Aerial_Survey_2017\2017_Shoreline_Images and F:\Norm\4.13_Assessing Gulf mangrove dieback\Gulf_Aerial_Survey_2019\2019_Shoreline_Images and I want the reprocessed imaged to be stored in E:\GOC_JCU_NESP-TWQ-4-13_Mangrove-Dieback_2017-2019\derived\2017_Shoreline_Images . 

There is additional information about each image stored in Shoreline_DB\NESP_GOC_AerialSurveys_2017_2019_Shoreline_DB.shp. This shapefile contains attributes '2017_Image' and '2019_Image' that contain the filename (no path) that the row of data corresponds to. The script should find the matching row of data for each image being processed. If no match is found an error message should be printed to a local log file and execution should continue. The shapefile also contains an attribute 'DivShort'. This is the name of the directory (but with no path) that output image should be stored in. I want the down sampled images to be saved into directories corresponding to the matching 'DivShort' for each photo. This will split the original files from a single directory per survey year into one directory per 'DivShort', reducing the number of photos per directory. The 'DivShort' directories and the output directories will no exists and so need to be created by the script. The script needs to print progress because there are many files to process. It should indicate how many of the images have been completed of the total sequence. 

This script should be restartable, so that if it is cancelled it can pickup from where it left off. This can be done by checking if an output image already exists then its processing can be skipped. To ensure this is reliable the image saving process should save to a temporary file that is renamed after the safe to the final name. This way if the script is cancelled mid save there will be no corrupted files.

**Follow up:**
I want the metadata in the images to be copied over including the Origin: Authors, Date taken, Camera settings and GPS location. I also want to set the Comments to: "This image is downscaled from the original photo. The original photos are available on request"

**Notes:** It turned out that the Comments field was causing a problem and so ChatGPT switch from using Pillow to Piexif library (that needed installing with: `pip install piexif`). The Comments field was not the field visible in the windows explorer. As it turns out the Comment field in Windows Explorer is not part of the file EXIF. I left in the comment setting code, and didn't switch back to Pillow as the script was working well enough. I dropped trying to set the comment field because this would not translate across file systems. I also added the generation of small thumbnails from the script. These are not used at this stage. 


# References:
Duke N.C., Mackenzie J., Kovacs J., Staben G., Coles, R., Wood A., & Castle Y. 2020. Assessing the Gulf of Carpentaria mangrove dieback 2017–2019. Volume 1: Aerial surveys. James Cook University, Townsville, 226 pp.
