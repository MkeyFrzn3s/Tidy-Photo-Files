import exifread
from opencage.geocoder import OpenCageGeocode

opencage_api_key = None

def set_opencage_api_key(api_key):
    global opencage_api_key
    opencage_api_key = api_key

def get_gps_coordinates(exif_data):
    lat = None
    lon = None

    if exif_data is None:
        return lat, lon

    if isinstance(exif_data, dict):  # piexif data
        gps_ifd = exif_data.get('GPS', {})
        gps_latitude = gps_ifd.get(2)  # GPSLatitude
        gps_latitude_ref = gps_ifd.get(1)  # GPSLatitudeRef
        gps_longitude = gps_ifd.get(4)  # GPSLongitude
        gps_longitude_ref = gps_ifd.get(3)  # GPSLongitudeRef

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degrees(gps_latitude, gps_latitude_ref)
            lon = convert_to_degrees(gps_longitude, gps_longitude_ref)
    else:  # exifread data
        gps_latitude = exif_data.get('GPS GPSLatitude')
        gps_latitude_ref = exif_data.get('GPS GPSLatitudeRef')
        gps_longitude = exif_data.get('GPS GPSLongitude')
        gps_longitude_ref = exif_data.get('GPS GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degrees_exifread(gps_latitude, gps_latitude_ref)
            lon = convert_to_degrees_exifread(gps_longitude, gps_longitude_ref)

    return lat, lon

def convert_to_degrees(value, ref):
    d, m, s = value
    degrees = d[0] / d[1] + (m[0] / m[1]) / 60 + (s[0] / s[1]) / 3600
    if ref in [b'S', b'W']:
        degrees = -degrees
    return degrees

def convert_to_degrees_exifread(value, ref):
    values = [float(v.num) / float(v.den) for v in value.values]
    degrees = values[0] + values[1] / 60 + values[2] / 3600
    if ref.values != 'N' and ref.values != 'E':
        degrees = -degrees
    return degrees

def reverse_geocode(lat, lon):
    geocoder = OpenCageGeocode(opencage_api_key)
    results = geocoder.reverse_geocode(lat, lon, language='en')

    if results and len(results) > 0:
        components = results[0].get('components', {})
        city_name = components.get('city', None)
        if city_name:
            return city_name

    return None
