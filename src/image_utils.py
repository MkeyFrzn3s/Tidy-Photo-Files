import cv2
import numpy as np
import hashlib
import os

def is_image_file(filename):
    return filename.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif'))

def is_video_file(filename):
    return filename.lower().endswith(('.mp4', '.avi', '.mov'))

def is_low_quality_image(image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)
    if image is None:
        return True  # Unable to read the image, consider it low quality

    # Assess image brightness (lower value indicates darker image)
    brightness = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).mean()

    # Define brightness threshold
    brightness_threshold = 25  # Adjust this value according to your preference

    return brightness < brightness_threshold

def hash_file(file_to_hash):
    BLOCK_SIZE = 65536
    hasher = hashlib.sha256()
    with open(file_to_hash, 'rb') as f:
        for block in iter(lambda: f.read(BLOCK_SIZE), b''):
            hasher.update(block)
    return hasher.hexdigest()
