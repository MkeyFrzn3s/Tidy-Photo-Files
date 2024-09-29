# metadata_utils.py

import os
import piexif
import exifread
from datetime import datetime
from image_utils import is_image_file
import piexif
import string

# Dictionary to keep track of the photo count for each camera on a given day
photo_count = {}

# List to keep track of files that were not moved
files_not_moved = []

# Temporary dictionary to store city names for non-image files
city_names_temp = {}

def get_exif_data(file_path):
    exif_data = {}
    if is_image_file(file_path):
        try:
            exif_data = piexif.load(file_path)
        except Exception as e:
            print(f"Error loading EXIF data with piexif: {e}")
            # Try using exifread as a fallback
            with open(file_path, 'rb') as f:
                try:
                    exif_data = exifread.process_file(f, details=False)
                except Exception as exifread_error:
                    print(f"Error loading EXIF data with exifread: {exifread_error}")
                    exif_data = {}
    else:
        # For non-image files or unsupported formats, return empty dict
        exif_data = {}
    return exif_data

def extract_capture_date(exif_data, file_path):
    capture_date = None
    if not exif_data:
        # No EXIF data found, fallback to file modification time
        print(f"No EXIF data found for file: {file_path}")
    else:
        if isinstance(exif_data, dict) and 'Exif' in exif_data:  # piexif data
            capture_date_str = exif_data['Exif'].get(piexif.ExifIFD.DateTimeOriginal, b'').decode('utf-8')
            if capture_date_str:
                try:
                    capture_date = datetime.strptime(capture_date_str, '%Y:%m:%d %H:%M:%S')
                except ValueError as e:
                    print(f"Error parsing capture date: {e}")
        else:  # exifread data
            for tag in ('EXIF DateTimeOriginal', 'EXIF DateTimeDigitized'):
                if tag in exif_data:
                    capture_date_str = str(exif_data[tag])
                    try:
                        capture_date = datetime.strptime(capture_date_str, '%Y:%m:%d %H:%M:%S')
                    except ValueError as e:
                        print(f"Error parsing capture date: {e}")
                    break

    if capture_date is None:
        # Fallback to file modification time
        modification_time = os.path.getmtime(file_path)
        capture_date = datetime.fromtimestamp(modification_time)

    return capture_date

def extract_camera_info(exif_data):
    camera_brand = 'Unknown'
    camera_model = 'Unknown'

    if isinstance(exif_data, dict):  # piexif data
        camera_model_bytes = exif_data.get('0th', {}).get(piexif.ImageIFD.Model, b'')
        camera_brand_bytes = exif_data.get('0th', {}).get(piexif.ImageIFD.Make, b'')
        if camera_model_bytes:
            camera_model = camera_model_bytes.decode('utf-8').strip()
        if camera_brand_bytes:
            camera_brand = camera_brand_bytes.decode('utf-8').strip()
    else:  # exifread data
        camera_model = str(exif_data.get('Image Model', 'Unknown')).strip()
        camera_brand = str(exif_data.get('Image Make', 'Unknown')).strip()

    # Remove invalid characters
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    camera_model = ''.join(c for c in camera_model if c in valid_chars)
    camera_brand = ''.join(c for c in camera_brand if c in valid_chars)

    return camera_brand, camera_model

def write_city_name(file_path, city_name):
    if is_image_file(file_path):
        write_city_to_metadata(file_path, city_name)
    else:
        write_city_to_temp(file_path, city_name)

def write_city_to_metadata(image_path, city_name):
    # Load the EXIF data using piexif
    try:
        exif_dict = piexif.load(image_path)
        # Convert city_name to bytes
        city_name_bytes = city_name.encode('utf-8')
        # Update the UserComment field
        exif_dict['Exif'][piexif.ExifIFD.UserComment] = city_name_bytes
        # Save the updated EXIF data back to the image
        piexif.insert(piexif.dump(exif_dict), image_path)
        print(f"City name '{city_name}' added to EXIF metadata.")
    except Exception as e:
        print(f"Error writing city name to metadata: {e}")

def write_city_to_temp(file_path, city_name):
    city_names_temp[file_path] = city_name

def get_photo_count(camera_model, capture_date):
    global photo_count
    date_key = capture_date.strftime('%Y-%m-%d')

    if camera_model not in photo_count:
        photo_count[camera_model] = {}

    if date_key not in photo_count[camera_model]:
        photo_count[camera_model][date_key] = 1
    else:
        photo_count[camera_model][date_key] += 1

    return str(photo_count[camera_model][date_key]).zfill(3)

def log_not_moved(filename, reason):
    files_not_moved.append((filename, reason))

def delete_temp_data():
    global city_names_temp
    city_names_temp = {}

def print_not_moved_files():
    print("Files that were not moved:")
    for filename, reason in files_not_moved:
        print(f"File: {filename}, Reason: {reason}")
    print(f"Total files not moved: {len(files_not_moved)}")
