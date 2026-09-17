import json
import requests

NOMINATIM_URL =   "https://nominatim.openstreetmap.org/search"

def get_location_coordinates(location: str) -> dict:
    """
    Geocode a place name into lat/lon using OpenStreetMap Nominatim.
    Raises ValueError if the location can't be found or the request fails.
    """

    try:
        params = {"q": location, "format":"jsonv2"}
        headers = {"User-Agent": "WeatherApp_LearningProject/1.0 (aakif.dev@gmail.com)"}

        r = requests.get(url=NOMINATIM_URL, params=params, headers=headers, timeout=10)

        if r.status_code != 200:
            raise ValueError(f"Geocoding failed: {r.status_code}")

        data = r.json()

        if not data:
            raise ValueError(f"Location not found: {location}")

        latitude = data[0]['lat']
        longitude = data[0]['lon']

        return {
            "latitude": latitude,
            "longitude": longitude
        }

    except Exception as e:
        raise ValueError(f"Location extraction failed: {e}")