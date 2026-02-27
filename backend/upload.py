# Import APIRouter to define API routes
# UploadFile & File are used to accept file uploads
# Depends is used for dependency injection (DB session)
# HTTPException is used to return custom error responses
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

# SQLAlchemy database session
from sqlalchemy.orm import Session

# Function that provides DB session
from database import get_db

# Import business logic (CSV processing logic)
import services


# Create router instance for upload-related APIs
router = APIRouter()


# ==========================================================
# FILE UPLOAD ENDPOINT
# ==========================================================
# This endpoint accepts CSV or Excel files containing
# employee punch/clock logs.
#
# Example:
# POST /upload
# Form-data → file = attendance_file.csv
@router.post("/upload")
async def upload_clock_logs(
    file: UploadFile = File(...),   # File is required (File(...) means mandatory)
    db: Session = Depends(get_db)   # Inject database session automatically
):
    
    # ------------------------------------------------------
    # FILE TYPE VALIDATION
    # ------------------------------------------------------
    # Only allow CSV or Excel files
    if not (
        file.filename.endswith('.csv') or 
        file.filename.endswith('.xlsx') or 
        file.filename.endswith('.xls')
    ):
        # Return 400 Bad Request if file format is invalid
        raise HTTPException(
            status_code=400, 
            detail="Only CSV or Excel files are allowed."
        )
    
    # ------------------------------------------------------
    # PROCESS FILE USING SERVICE LAYER
    # ------------------------------------------------------
    # Calls async function in services.py to:
    #   - Read file
    #   - Clean data
    #   - Sync employees
    #   - Insert clock logs
    result = await services.process_csv_upload(file, db)

    # Return success response
    return {
        "message": "File processed successfully",
        "data": result
    }
