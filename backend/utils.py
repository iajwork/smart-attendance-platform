import math
import pandas as pd

# ==========================================================
# GEO-FENCING FUNCTION
# ==========================================================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Helper function to calculate Haversine distance in meters."""
    R = 6371000  # Earth radius in meters
    
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def get_location_status(lat: float, lon: float, all_office_locations: list) -> str:
    """
    Checks the employee's lat/lon against a list of ALL valid office locations.
    If they are within the radius of ANY office, return the specific office name.
    """
    # ------------------------------------------------------
    # BASIC VALIDATION
    # ------------------------------------------------------
    if pd.isna(lat) or pd.isna(lon) or lat == 0 or lon == 0:
        return "REMOTE"
        
    # ------------------------------------------------------
    # CHECK AGAINST ALL OFFICES
    # ------------------------------------------------------
    for office in all_office_locations:
        office_lat = office.get('lat')
        office_lon = office.get('lon')
        radius = office.get('radius', 100)
        office_name = office.get('name') # <--- We grab the specific name here
        
        if pd.isna(office_lat) or pd.isna(office_lon):
            continue
            
        distance = calculate_distance(lat, lon, office_lat, office_lon)
        
        if distance <= radius:
            return office_name # <--- Return "Seagate - Pune" instead of "In office"
            
    # If no matches were found after checking all offices
    return "REMOTE"
