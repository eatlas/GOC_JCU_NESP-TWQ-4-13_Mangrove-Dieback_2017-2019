import os
import logging
import geopandas as gpd
from PIL import Image
from PIL import ExifTags
import piexif

# Configure logging
logging.basicConfig(filename='process_images.log', level=logging.ERROR)

# Load the shapefile
shapefile_path = "..\\derived\\Shoreline_DB\\GOC_NESP-4-13_JCU_AerialSurveys_2017_2019_Shoreline_DB.shp"
print("Reading Shoreline_DB")
df = gpd.read_file(shapefile_path)

print("Checking for duplicates in file names")
# Check for duplicates in 2017_Image and 2019_Image
duplicates_2017 = df[df['2017_Image'].duplicated(keep=False)]
duplicates_2019 = df[df['2019_Image'].duplicated(keep=False)]

if not duplicates_2017.empty:
    logging.error(f"Duplicates found in 2017_Image: {duplicates_2017['2017_Image'].tolist()}")
if not duplicates_2019.empty:
    logging.error(f"Duplicates found in 2019_Image: {duplicates_2019['2019_Image'].tolist()}")

# Index the shapefile data by image filename for both years, ignoring duplicates
index_2017 = df.drop_duplicates(subset='2017_Image', keep='first').set_index('2017_Image').to_dict(orient='index')
index_2019 = df.drop_duplicates(subset='2019_Image', keep='first').set_index('2019_Image').to_dict(orient='index')


def create_thumbnail(image, thumbnail_size=(100, 100)):
    """
    Create a thumbnail image with specified size.
    """
    # Calculate the aspect ratio of the image
    aspect = image.width / image.height

    # Determine the new dimensions for the square crop
    if aspect > 1:  # Width greater than height
        new_width = int(aspect * thumbnail_size[1])
        new_height = thumbnail_size[1]
        image = image.resize((new_width, new_height), Image.LANCZOS)
    else:  # Height greater than width
        new_width = thumbnail_size[0]
        new_height = int(thumbnail_size[0] / aspect)
        image = image.resize((new_width, new_height), Image.LANCZOS)

    # Calculate the coordinates for the center crop
    left = (image.width - thumbnail_size[0]) / 2
    top = (image.height - thumbnail_size[1]) / 2
    right = (image.width + thumbnail_size[0]) / 2
    bottom = (image.height + thumbnail_size[1]) / 2

    # Perform the center crop and return the thumbnail image
    image = image.crop((left, top, right, bottom))
    return image



def copy_exif_data(original_image_path, modified_image, comments, temp_file):
    """
    Copy EXIF data from the original image to the modified image and update the comments.
    """
    # Load EXIF data from the original image
    exif_dict = piexif.load(original_image_path)

    # Update the 'UserComment' field
    if piexif.ExifIFD.UserComment in exif_dict["Exif"]:
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = comments.encode('utf-8')
    else:
        # If 'UserComment' tag doesn't exist, create it
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(comments)

    # Dump the EXIF data back to bytes
    exif_bytes = piexif.dump(exif_dict)

    # Save the modified image with the updated EXIF
    modified_image.save(temp_file, "JPEG", quality=85, exif=exif_bytes)

def process_images(folder_path, year_index, base_output, thumbnail_output):
    total_files = len(os.listdir(folder_path))
    for idx, image_name in enumerate(os.listdir(folder_path)):
        #try:
            # Check if image already exists
            div_short = year_index.get(image_name, {}).get('DivShort')
            if div_short is None:
                logging.error(f"Couldn't find a match for image {image_name}.")
                continue

            output_folder = os.path.join(base_output, div_short)
            os.makedirs(output_folder, exist_ok=True)

            output_image_path = os.path.join(output_folder, image_name)
            if os.path.exists(output_image_path):
                print(f"Skipped {idx + 1}/{total_files}: {image_name}")
                continue
                
            image_path = os.path.join(folder_path, image_name)
            print(f"Opening image: {image_path}")
            with Image.open(image_path) as img:
                img.thumbnail((3000, 2000), Image.LANCZOS)
                
                # Set comments
                comments = "This image is downscaled from the original photo. The original photos are available on request"
                # Create thumbnail
                thumbnail_image = create_thumbnail(img)
                thumbnail_folder = os.path.join(thumbnail_output, div_short)
                os.makedirs(thumbnail_folder, exist_ok=True)
                thumbnail_image_path = os.path.join(thumbnail_folder, image_name)
                thumbnail_image.save(thumbnail_image_path, "JPEG", quality=85) 
                
                output_folder = os.path.join(base_output, div_short)
                os.makedirs(output_folder, exist_ok=True)
                
                temp_file = os.path.join(output_folder, f"{image_name}.temp")
                
                # Copy EXIF data and save the image
                #print("Copying EXIF")
                copy_exif_data(image_path, img, comments, temp_file)
                
                #print("Renaming file")
                final_image_path = os.path.join(output_folder, image_name)
                os.rename(temp_file, final_image_path)
                
                print(f"Processed {idx + 1}/{total_files}: {image_name}")

        #except Exception as e:
        #    logging.error(f"Error processing {image_name}. Error: {str(e)}")

input_base_path = "F:\\Norm\\4.13_Assessing Gulf mangrove dieback"
output_base_path = "E:\\GOC_JCU_NESP-TWQ-4-13_Mangrove-Dieback_2017-2019\\derived"

print("Started processing 2017 data")
# Process 2017 images
process_images(f"{input_base_path}\\Gulf_Aerial_Survey_2017\\2017_Shoreline_Images", 
               index_2017, 
               f"{output_base_path}\\images\\2017_Shoreline",
               f"{output_base_path}\\thumbnails\\2017_Shoreline")

print("Started processing 2019 data")
# Process 2019 images - modify paths as per your requirements
process_images(f"{input_base_path}\\Gulf_Aerial_Survey_2019\\2019_Shoreline_Images", 
               index_2019, 
               f"{output_base_path}\\images\\2019_Shoreline",
               f"{output_base_path}\\thumbnails\\2019_Shoreline")

print("Processing completed!")
