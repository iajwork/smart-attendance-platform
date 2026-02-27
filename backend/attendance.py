# Import APIRouter to create route groups
# Depends is used for dependency injection (like DB connection)
from fastapi import APIRouter, Depends

# SQLAlchemy Session object for database operations
from sqlalchemy.orm import Session

# get_db function provides database session
from database import get_db

# Import business logic functions from services layer
import services

# Used to handle date input from API
from datetime import date


# Create a router object
# This helps us separate routes (clean architecture)
router = APIRouter()


# ------------------------------
# DAILY ATTENDANCE PROCESSING API
# ------------------------------
# This endpoint will process attendance for ONE specific date
# Example request:
# POST /process-attendance?target_date=2026-02-25
@router.post("/process-attendance")
def process_daily_attendance(
    target_date: date,                     # Date passed as query parameter
    db: Session = Depends(get_db)          # Inject database session automatically
):
    # Call service layer function to calculate attendance
    # We pass date + database session
    result = services.calculate_daily_attendance(target_date, db)

    # Return success message with number of records updated
    return {
        "message": f"Attendance processed for {target_date}",
        "records_updated": result
    }


# ------------------------------
# MONTHLY ATTENDANCE PROCESSING API
# ------------------------------
# This endpoint processes attendance for ENTIRE month
# Example request:
# POST /process-month?month=2&year=2026
@router.post("/process-month")
def process_month_api(
    month: int,                            # Month number (1-12)
    year: int,                             # Year (e.g., 2026)
    db: Session = Depends(get_db)          # Inject database session
):
    # Call service layer function to process full month attendance
    result = services.process_entire_month(month, year, db)

    # Return confirmation message with processed data
    return {
        "message": f"Successfully processed all attendance for {month}/{year}",
        "data": result
    }}
