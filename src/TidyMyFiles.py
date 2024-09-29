import os

from file_utils import process_files, delete_empty_folders
from geocode_utils import set_opencage_api_key
from jpg_metadata_utils import delete_temp_data, print_not_moved_files

def main():
    # Prompt the user to enter the source folder
    source_folder = input("source folder path")
    # source_folder = "xyz"  # Uncomment and set a fixed source folder if convenient

    # Prompt the user to enter the destination folder
    destination_folder = input("destination folder path")
    # destination_folder = "xyz"  # Uncomment and set a fixed destination folder if convenient

    # OpenCage Geocoder API key
    opencage_api_key = input ("open cage API key")
    # opencage_api_key = 'xyz'  # Uncomment and set a fixed OpenCage API key if convenient

    # Set the API key in the geocode_utils module
    set_opencage_api_key(opencage_api_key)

    # Start processing files in the source folder and its sub-folders
    process_files(source_folder, destination_folder)

    # Delete empty folders after moving the files
    delete_empty_folders(source_folder)

    # After moving files, remove the temporary dictionary for city names
    delete_temp_data()

    # Print the list of files that were not moved and the reasons for the failure
    print_not_moved_files()

    # The End!!!

if __name__ == "__main__":
    main()
