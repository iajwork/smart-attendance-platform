import math
import pandas as pd

OFFICE_LAT = 19.0760
OFFICE_LON = 72.8777
OFFICE_RADIUS = 100 

def get_attendance_status(lat: float, lon: float) -> str:
    if pd.isna(lat) or pd.isna(lon) or lat == 0 or lon == 0:
        return "INVALID"

    R = 6371000 
    lat1, lon1 = math.radians(OFFICE_LAT), math.radians(OFFICE_LON)
    lat2, lon2 = math.radians(lat), math.radians(lon)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return "IN_OFFICE" if distance <= OFFICE_RADIUS else "REMOTE"
