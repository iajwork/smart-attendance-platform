# Import APIRouter to define API routes
# Depends is used for dependency injection (like DB session)
# Response is used to manually return custom responses (like CSV file)
from fastapi import APIRouter, Depends, Response

# SQLAlchemy session for database operations
from sqlalchemy.orm import Session

# get_db provides database session
from database import get_db

# Import business logic functions from services layer
import services


# Create router instance
router = APIRouter()


# ==========================================================
# DAILY REPORT DOWNLOAD API
# ==========================================================
# Endpoint to download daily attendance report as CSV
# Example:
# GET /reports/daily?target_date=2026-02-26
@router.get("/reports/daily")
def get_daily_report(
    target_date: str,                     # Date passed as query parameter (YYYY-MM-DD)
    db: Session = Depends(get_db)         # Inject database session
):
    # Call service function to generate CSV data (as string)
    csv_data = services.fetch_daily_report_csv(target_date, db)

    # Return CSV as downloadable file
    return Response(
        content=csv_data,                 # Actual CSV content
        media_type="text/csv",            # Tell browser this is a CSV file
        headers={
            # Forces browser to download file instead of displaying it
            "Content-Disposition": f"attachment; filename=Daily_Attendance_{target_date}.csv"
        }
    )


# ==========================================================
# MONTHLY SUMMARY DOWNLOAD API
# ==========================================================
# Endpoint to download monthly attendance summary as CSV
# Example:
# GET /reports/monthly?month=2&year=2026
@router.get("/reports/monthly")
def get_monthly_summary(
    month: int,                           # Month number (1-12)
    year: int,                            # Year (e.g., 2026)
    db: Session = Depends(get_db)         # Inject database session
):
    # Call service function to generate monthly summary CSV
    csv_data = services.fetch_monthly_summary_csv(month, year, db)

    # Return CSV file as downloadable response
    return Response(
        content=csv_data,                 # CSV content as string
        media_type="text/csv",            # Set content type
        headers={
            # Custom filename for downloaded file
            "Content-Disposition": f"attachment; filename=Monthly_Summary_{month}_{year}.csv"
        }
    )
