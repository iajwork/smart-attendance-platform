import math
import pandas as pd
# ==========================================================
# GEO-FENCING FUNCTION
# ==========================================================
# This function calculates whether an employee's punch
# location is inside the allowed office radius.
# It uses the Haversine Formula to calculate
# distance between two latitude-longitude points.

def get_location_status(lat: float, lon: float, office_lat: float, office_lon: float, radius: int) -> str:
    # Return "REMOTE" if coordinates are missing or bad
    # ------------------------------------------------------
    # BASIC VALIDATION
    # ------------------------------------------------------
    # If employee coordinates are missing or invalid,
    # treat as REMOTE punch
    if pd.isna(lat) or pd.isna(lon) or lat == 0 or lon == 0:
        return "REMOTE"
    # If office location is missing,
    # we cannot calculate distance → treat as REMOTE
    if pd.isna(office_lat) or pd.isna(office_lon):
        return "REMOTE"
    # ------------------------------------------------------
    # HAVERSINE FORMULA (Distance on Earth's surface)
    # ------------------------------------------------------

    R = 6371000 # Earth radius in meters
    # Convert latitude & longitude from degrees → radians

    lat1, lon1 = math.radians(office_lat), math.radians(office_lon)
    lat2, lon2 = math.radians(lat), math.radians(lon)
    # Differences between coordinates

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Haversine calculation
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Final distance between office and employee location
    distance = R * c
    # ------------------------------------------------------
    # RADIUS CHECK
    # ------------------------------------------------------
    # If distance is within allowed radius → In office

    if distance <= radius:
        return "In office"
    else: 
        return "REMOTE"
