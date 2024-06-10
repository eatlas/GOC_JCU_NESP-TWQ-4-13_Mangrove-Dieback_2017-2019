import os
import shutil
import logging
from PIL import Image
import piexif

# Constants
INPUT_DIR_2017 = r"F:\Norm\4.13_Assessing Gulf mangrove dieback\Gulf_Aerial_Survey_2017\0_general images"
INPUT_DIR_2019 = r"F:\Norm\4.13_Assessing Gulf mangrove dieback\Gulf_Aerial_Survey_2019\0_general images"
OUTPUT_DIR_2017 = r"..\public\images\2017_general_images"
OUTPUT_DIR_2019 = r"..\public\images\2019_general_images"
MAX_WIDTH = 3600
MAX_HEIGHT = 2391
JPEG_QUALITY = 85
USER_COMMENT = "This image is downscaled from the original photo. From dataset https://doi.org/10.26274/1ef5-4147"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_output_directories():
    os.makedirs(OUTPUT_DIR_2017, exist_ok=True)
    os.makedirs(OUTPUT_DIR_2019, exist_ok=True)

def resize_image(input_path, output_path):
    img = Image.open(input_path)

    # Check if EXIF data exists
    if 'exif' in img.info:
        exif_dict = piexif.load(img.info['exif'])
        user_comment_encoded = USER_COMMENT.encode('utf-16')
        exif_dict['Exif'][piexif.ExifIFD.UserComment] = user_comment_encoded
        exif_bytes = piexif.dump(exif_dict)
    else:
        exif_bytes = None

    original_width, original_height = img.size
    ratio = min(MAX_WIDTH / original_width, MAX_HEIGHT / original_height)
    new_size = (int(original_width * ratio), int(original_height * ratio))

    img = img.resize(new_size, Image.LANCZOS)

    if exif_bytes:
        img.save(output_path, "JPEG", quality=JPEG_QUALITY, exif=exif_bytes)
    else:
        img.save(output_path, "JPEG", quality=JPEG_QUALITY)

def count_total_files(input_dir):
    total_files = 0
    for root, _, files in os.walk(input_dir):
        total_files += len(files)
    return total_files

def process_directory(input_dir, output_dir):
    total_files = count_total_files(input_dir)
    processed_files = 0

    for root, _, files in os.walk(input_dir):
        for file in files:
            input_path = os.path.join(root, file)
            relative_path = os.path.relpath(input_path, input_dir)
            output_path = os.path.join(output_dir, relative_path)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                resize_image(input_path, output_path)
            else:
                shutil.copy2(input_path, output_path)

            processed_files += 1
            logging.info(f"Processing {processed_files} of {total_files} images in {input_dir}")

if __name__ == "__main__":
    logging.info("Script started.")
    create_output_directories()
    process_directory(INPUT_DIR_2017, OUTPUT_DIR_2017)
    process_directory(INPUT_DIR_2019, OUTPUT_DIR_2019)
    logging.info("Script finished.")
