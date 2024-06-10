import os
import pandas as pd
import shapefile
import piexif
from PIL import Image
from concurrent.futures import ProcessPoolExecutor, as_completed
import signal
import sys

# Define paths and constants
shapefile_path = "..\\public\\Shoreline_DB\\GOC_NESP-4-13_JCU_AerialSurveys_2017_2019_Shoreline_DB.shp"
base_output_dir_2017 = '../public/images/2017_Shoreline/'
base_output_dir_2019 = '../public/images/2019_Shoreline/'
image_path_2017 = 'F:\\Norm\\4.13_Assessing Gulf mangrove dieback\\Gulf_Aerial_Survey_2017\\2017_Shoreline_Images'
image_path_2019 = 'F:\\Norm\\4.13_Assessing Gulf mangrove dieback\\Gulf_Aerial_Survey_2019\\2019_Shoreline_Images'
max_size = (3600, 2391)
jpeg_quality = 85
user_comment = "This image is downscaled from the original photo. From dataset https://doi.org/10.26274/1ef5-4147"

def load_shapefile(shapefile_path):
    print("Loading shapefile...")
    sf = shapefile.Reader(shapefile_path)
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shapes = sf.shapes()
    df = pd.DataFrame(columns=fields, data=records)
    df['coords'] = [shape.points for shape in shapes]
    print("Shapefile loaded successfully.")
    return df

def check_discrepancies(df):
    print("Checking for discrepancies...")
    discrepancies = []
    for i, (_, row) in enumerate(df.iterrows()):
        if i % 500 == 0:
            print(f"Checked {i} images...")
        if row['2017_Image']:
            if not os.path.exists(os.path.join(image_path_2017, row['2017_Image'])):
                discrepancies.append(row['2017_Image'])
        if row['2019_Image']:
            if not os.path.exists(os.path.join(image_path_2019, row['2019_Image'])):
                discrepancies.append(row['2019_Image'])
    if discrepancies:
        print("Discrepancies found:")
        for discrepancy in discrepancies:
            print(f"Missing image: {discrepancy}")
        return False
    print("No discrepancies found.")
    return True

def process_image(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            if img.size[0] <= max_size[0] and img.size[1] <= max_size[1]:
                img.save(output_path, "JPEG", quality=jpeg_quality)
                print(f"Copied image without resizing: {input_path}")
                return
            img.thumbnail(max_size, Image.LANCZOS)
            exif_dict = piexif.load(img.info["exif"])
            # Update the 'UserComment' field
            if piexif.ExifIFD.UserComment in exif_dict["Exif"]:
                exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment.encode('utf-8')
            else:
                # If 'UserComment' tag doesn't exist, create it
                exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(user_comment)
            #exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(user_comment)
            exif_bytes = piexif.dump(exif_dict)
            img.save(output_path, "JPEG", quality=jpeg_quality, exif=exif_bytes)
            print(f"Processed image: {input_path}")
    except Exception as e:
        print(f"Error processing image {input_path}: {e}")

def process_images(df, year, base_output_dir, image_path):
    for i, row in df.iterrows():
        print(f"Processing image {i + 1} of {len(df)} for year {year}...")
        image_attr = f"{year}_Image"
        image_file = row[image_attr]
        if not image_file:
            continue
        group_range = row['GroupRange']
        shore_fid = row['Shore_FID']
        output_dir = os.path.join(base_output_dir, group_range)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, image_file)
        if os.path.exists(output_path):
            print(f"Skipped already processed image: {output_path}")
            continue
        input_path = os.path.join(image_path, image_file)
        process_image(input_path, output_path)

def generate_readme(df, base_output_dir):
    group_ranges = df['GroupRange'].unique()
    for group_range in group_ranges:
        group_df = df[df['GroupRange'] == group_range]
        mid_row = group_df.iloc[len(group_df) // 2]
        longitude, latitude = mid_row['Shore_X'], mid_row['Shore_Y']
        readme_text = (
            f"Where are these photos? View this group of photos on an "
            f"[interactive map](https://maps.eatlas.org.au/index.html?intro=false&z=13&ll={longitude},{latitude}"
            f"&l0=ea_nesp4%3AGOC_NESP-4-13_JCU_AerialSurveys_2017_2019_Shoreline_DB,ea_ea-be%3AWorld_Bright-Earth-e-Atlas-basemap,"
            f"google_HYBRID,google_TERRAIN,ea_nesp-mac-3%3AAU_NESP-MaC-3-17_AIMS_S2-comp_low-tide_p30-trueColour&v0=,f,,f)\n"
            f"Imagery from [Gulf of Carpentaria Mangrove Aerial Shoreline Surveys 2017 & 2019](https://doi.org/10.26274/1ef5-4147)"
        )
        output_dir = os.path.join(base_output_dir, group_range)
        if not os.path.exists(output_dir):
            print(f"Skipping generating readme.md as no output directory: {output_dir}")
            continue
            
        with open(os.path.join(output_dir, 'readme.md'), 'w') as f:
            f.write(readme_text)
        print(f"Generated readme.md for group range {group_range}")

def main():
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C! Exiting gracefully...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("Starting script...")
    df = load_shapefile(shapefile_path)
    if not check_discrepancies(df):
        print("Discrepancies found. Stopping script.")
        return

    with ProcessPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(process_images, df, 2017, base_output_dir_2017, image_path_2017)
        future2 = executor.submit(process_images, df, 2019, base_output_dir_2019, image_path_2019)

        for future in as_completed([future1, future2]):
            try:
                future.result()
            except Exception as exc:
                print(f"Generated an exception: {exc}")

    generate_readme(df, base_output_dir_2017)
    generate_readme(df, base_output_dir_2019)
    print("Script completed.")

if __name__ == "__main__":
    main()
