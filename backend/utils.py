import math
import pandas as pd

def is_within_geofence(lat: float, lon: float, office_lat: float, office_lon: float, radius: int) -> bool:
    """Calculates if a given lat/lon is within the dynamic office radius. Returns Boolean."""
    if pd.isna(lat) or pd.isna(lon) or lat == 0 or lon == 0:
        return False
        
    if pd.isna(office_lat) or pd.isna(office_lon):
        return False # Failsafe if employee has no assigned location

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
    else
        return "REMOTE"
