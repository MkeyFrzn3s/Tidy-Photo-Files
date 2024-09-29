import os
import shutil

from jpg_metadata_utils import (
    get_exif_data,
    extract_capture_date,
    extract_camera_info,
    write_city_name,
    get_photo_count,
    log_not_moved,
)
from image_utils import (
    is_image_file,
    is_video_file,
    is_low_quality_image,
    hash_file,
)

import string
from geocode_utils import reverse_geocode, get_gps_coordinates

# Dictionary to keep track of file hashes to handle duplicates
file_hashes = {}

def process_files(source_folder, destination_folder):
    for root, dirs, files in os.walk(source_folder):
        for filename in files:
            file_path = os.path.join(root, filename)

            if is_image_file(filename) or is_video_file(filename):
                # Calculate the hash of the file content
                file_hash = hash_file(file_path)

                # Check if the file is a duplicate based on content
                if file_hash in file_hashes:
                    # Remove the duplicate file
                    try:
                        os.remove(file_path)
                        print(f"Removed duplicate file: {file_path}")
                        log_not_moved(filename, "Duplicate - Removed")
                    except FileNotFoundError:
                        pass  # If the file was already deleted
                    continue
                else:
                    file_hashes[file_hash] = file_path

                if is_image_file(filename) and is_low_quality_image(file_path):
                    log_not_moved(filename, "Low Quality")
                    continue  # Skip further processing

                exif_data = get_exif_data(file_path)
                capture_date = extract_capture_date(exif_data, file_path)
                camera_brand, camera_model = extract_camera_info(exif_data)

                lat, lon = get_gps_coordinates(exif_data)
                city_name = None
                if lat and lon:
                    city_name = reverse_geocode(lat, lon)
                    if city_name:
                        write_city_name(file_path, city_name)

                new_filename = generate_new_filename(
                    capture_date, camera_brand, camera_model, city_name, filename
                )

                # Create destination folder
                destination_path = create_destination_path(
                    destination_folder, capture_date, new_filename
                )

                # Move the file to the new location
                try:
                    shutil.move(file_path, destination_path)
                    print(f"Moved {filename} to {destination_path}")
                except shutil.Error as e:
                    log_not_moved(filename, str(e))
            else:
                log_not_moved(filename, "Unsupported file type")

def create_destination_path(destination_folder, capture_date, new_filename):
    year = str(capture_date.year)
    month = str(capture_date.month).zfill(2)
    day = str(capture_date.day).zfill(2)

    destination_year_folder = os.path.join(destination_folder, year)
    destination_month_folder = os.path.join(destination_year_folder, month)
    os.makedirs(destination_month_folder, exist_ok=True)

    destination_path = os.path.join(destination_month_folder, new_filename)
    if os.path.exists(destination_path):
        new_filename = resolve_duplicate_filename(destination_month_folder, new_filename)
        destination_path = os.path.join(destination_month_folder, new_filename)

    return destination_path

def generate_new_filename(capture_date, camera_brand, camera_model, city_name, original_filename):
    file_extension = os.path.splitext(original_filename)[1]
    year = capture_date.strftime('%Y')
    month = capture_date.strftime('%m')
    day = capture_date.strftime('%d')

    new_filename = f"{year}_{month}_{day}_"

    if camera_brand != 'Unknown':
        new_filename += f"{camera_brand}_"

    new_filename += f"{camera_model}"

    if city_name:
        new_filename += f"_{city_name}"

    photo_count = get_photo_count(camera_model, capture_date)
    new_filename += f"_{photo_count}{file_extension}"

    # Remove any invalid characters from the filename
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    new_filename = ''.join(c for c in new_filename if c in valid_chars)

    return new_filename

def resolve_duplicate_filename(destination_folder, filename):
    file_name, file_extension = os.path.splitext(filename)
    counter = 1

    while True:
        new_filename = f"{file_name}_{counter}{file_extension}"
        if not os.path.exists(os.path.join(destination_folder, new_filename)):
            return new_filename
        counter += 1

def delete_empty_folders(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if not os.listdir(folder_path):
                os.rmdir(folder_path)
