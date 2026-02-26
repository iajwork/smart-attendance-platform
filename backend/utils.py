import math
import pandas as pd

def get_location_status(lat: float, lon: float, office_lat: float, office_lon: float, radius: int) -> str:
    # Return "REMOTE" instead of False if coordinates are bad
    if pd.isna(lat) or pd.isna(lon) or lat == 0 or lon == 0:
        return "REMOTE"
        
    if pd.isna(office_lat) or pd.isna(office_lon):
        return "REMOTE"

    R = 6371000 # Earth radius in meters
    lat1, lon1 = math.radians(office_lat), math.radians(office_lon)
    lat2, lon2 = math.radians(lat), math.radians(lon)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    if distance <= radius:
        return "In office"
    else: # <--- Missing colon fixed here!
        return "REMOTE"
