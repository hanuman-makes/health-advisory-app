"""
appointment_finder.py - Helps find nearby doctors using free APIs
"""

import requests
import urllib.parse

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# User-Agent required by Nominatim policy
HEADERS = {
    'User-Agent': 'MediSense Health Advisory System (https://github.com/your-repo/medisense)'
}

def geocode_location(location_query):
    """
    Convert a location query (city, address) to latitude and longitude using Nominatim.
    Returns (lat, lon) or None if not found.
    """
    params = {
        'q': location_query,
        'format': 'json',
        'limit': 1
    }
    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None

def generate_doctors_search_url(location_query, radius_km=5):
    """
    Generate a Google Maps search URL for doctors near the given location.
    Does not require API key; just opens Google Maps with search query.
    """
    # URL encode the query
    query = f"doctors near {location_query}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/maps/search/{encoded_query}"
    return url

def get_nearby_doctors_info(location_query):
    """
    Attempt to get nearby doctors using Overpass API (more complex).
    For simplicity, we just provide the Google Maps link.
    Returns a dict with search URL and optional geocoded coordinates.
    """
    coords = geocode_location(location_query)
    search_url = generate_doctors_search_url(location_query)
    return {
        'location_query': location_query,
        'coordinates': coords,
        'doctors_search_url': search_url
    }

# Example usage (commented out)
# if __name__ == "__main__":
#     info = get_nearby_doctors_info("New York, NY")
#     print(info)