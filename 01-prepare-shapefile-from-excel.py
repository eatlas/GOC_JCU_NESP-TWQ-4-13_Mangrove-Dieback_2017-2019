import os
import shutil
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

base_path = 'E:/Norm/4.13_Assessing Gulf mangrove dieback'
# Function to check if files exist
# Function to check if files exist
def check_file_availability(df, column, base_path):
    print(f"Checking availability of files in '{column}' column...")
    missing_files_count = 0
    total_files = len(df)
    
    for idx, row in df.iterrows():
        file = row[column]
        if pd.notna(file) and not os.path.isfile(os.path.join(base_path, str(file))):
            df.at[idx, column] = None
            missing_files_count += 1
        if (idx + 1) % 500 == 0 or idx == total_files - 1:
            print(f"Checked {idx + 1}/{total_files} files...")

    print(f"Total missing files in '{column}': {missing_files_count}")
    return df

# Start of the script
print("Script started...")

# Load the Excel file
file_path = f'{base_path}/Gulf_Aerial_Survey_2017/NESP_GOC_AerialSurveys_2017_2019.xlsx'
print(f"Loading Excel file from {file_path}...")

sheet_db = 'Shoreline_Image_Database_17_19'
sheet_map = 'Shore_Dieback_MAP'

print(f"Reading sheet '{sheet_db}'...")
df_db = pd.read_excel(file_path, sheet_name=sheet_db)
print(f"Reading sheet '{sheet_map}'...")
df_map = pd.read_excel(file_path, sheet_name=sheet_map)

# Select and rename columns
print("Selecting and renaming columns...")
df_db = df_db[['Shore_FID', 'Shore_X', 'Shore_Y', '2017_Image', '2019_Image']]
df_map = df_map[['Shore_FID', 'Image_ID_2017', 'Image_ID_2019', 'X_2017', 'X_2019', 'Shore_Mangrove', 'Density', 'Type', 'Dieback']]
df_map.rename(columns={
    'Image_ID_2017': 'ImgID_2017',
    'Image_ID_2019': 'ImgID_2019',
    'Shore_Mangrove': 'Shore_Mang'
}, inplace=True)

# Remove rows where 'Shore_X' or 'Shore_Y' is blank
print("Removing rows where 'Shore_X' or 'Shore_Y' is blank...")
df_db = df_db.dropna(subset=['Shore_X', 'Shore_Y'])

# Check file availability
df_db = check_file_availability(df_db, '2017_Image', f'{base_path}/Gulf_Aerial_Survey_2017/2017_Shoreline_Images')
df_db = check_file_availability(df_db, '2019_Image', f'{base_path}/Gulf_Aerial_Survey_2019/2019_Shoreline_Images')

# Remove rows where both '2017_Image' and '2019_Image' are NULL
print("Removing rows where both '2017_Image' and '2019_Image' are NULL...")
df_db = df_db.dropna(subset=['2017_Image', '2019_Image'], how='all')

# Join the dataframes on Shore_FID
print("Joining dataframes on 'Shore_FID'...")
df = pd.merge(df_db, df_map, on='Shore_FID', how='left')

# Calculate ImageCount
print("Calculating 'ImageCount'...")
df['ImageCount'] = df[['2017_Image', '2019_Image']].notnull().sum(axis=1)

# Calculate LabelScale
print("Calculating 'LabelScale'...")
df['LabelScale'] = 10
multiples = [5, 10, 20, 50, 100, 200, 500, 1000, 2000]
for multiple in multiples:
    df.loc[df['Shore_FID'] % multiple == 0, 'LabelScale'] = 10 - (multiples.index(multiple) + 1)

# Calculate GroupID and GroupRange
print("Calculating 'GroupID' and 'GroupRange'...")
df['GroupID'] = df['Shore_FID'] // 250
df['GroupRange'] = df['GroupID'].apply(lambda x: f'{max(x*250, df["Shore_FID"].min())}-{min((x+1)*250-1, df["Shore_FID"].max())}')

# Create geometry column
print("Creating geometry column...")
geometry = [Point(xy) for xy in zip(df['Shore_X'], df['Shore_Y'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Load the polygons shapefile
polygons_path = '../new-data/GOC_AIMS_Shore-drainage-divisions.shp'
print(f"Loading polygons shapefile from {polygons_path}...")
polygons = gpd.read_file(polygons_path)

# Perform spatial join to add 'Division' and 'DivShort' attributes
print("Performing spatial join...")
gdf = gpd.sjoin(gdf, polygons[['Division', 'DivShort', 'geometry']], how='left', op='within')

# Drop the 'index_right' column
print("Dropping 'index_right' column...")
gdf = gdf.drop(columns=['index_right'])

# Print the columns of the GeoDataFrame after the join and drop
print("Columns after dropping 'index_right':", gdf.columns)

# Ensure the output directory exists
output_dir = '../public/Shoreline_DB'
print(f"Ensuring the output directory exists at {output_dir}...")
os.makedirs(output_dir, exist_ok=True)

# Define the schema with controlled text lengths
schema = {
    'geometry': 'Point',
    'properties': {
        'Shore_FID': 'int:10',
        'Shore_X': 'float',
        'Shore_Y': 'float',
        '2017_Image': 'str:30',
        '2019_Image': 'str:30',
        'ImgID_2017': 'str:30',
        'ImgID_2019': 'str:30',
        'X_2017': 'str:5',
        'X_2019': 'str:5',
        'Shore_Mang': 'int:1',
        'Density': 'int:1',
        'Type': 'int:1',
        'Dieback': 'int:1',
        'ImageCount': 'int:10',
        'LabelScale': 'int:10',
        'GroupID': 'int:10',
        'GroupRange': 'str:30',
        'Division': 'str:25',
        'DivShort': 'str:25'
    }
}

# Print the schema for debugging
print("Schema defined for the shapefile:", schema)

# Save as shapefile with the defined schema
output_path = os.path.join(output_dir, 'GOC_NESP-4-13_JCU_AerialSurveys_2017_2019_Shoreline_DB.shp')
print(f"Saving the GeoDataFrame as a shapefile to {output_path}...")
gdf.to_file(output_path, driver='ESRI Shapefile', schema=schema)

# Copy the input Excel file and polygons shapefile to the output directory
print("Copying input files to the output directory...")
shutil.copy(file_path, output_dir)

# Copy all components of the shapefile
shapefile_components = ['shp', 'shx', 'dbf', 'prj']
for component in shapefile_components:
    src = f'../new-data/GOC_AIMS_Shore-drainage-divisions.{component}'
    dst = os.path.join(output_dir, f'GOC_AIMS_Shore-drainage-divisions.{component}')
    shutil.copy(src, dst)

# End of the script
print("Shapefile and input files copied successfully.")
print("Script completed.")
