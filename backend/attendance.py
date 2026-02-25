from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import services
from datetime import date

router = APIRouter()

@router.post("/process-attendance")
def process_daily_attendance(target_date: date, db: Session = Depends(get_db)):
    result = services.calculate_daily_attendance(target_date, db)
    return {"message": f"Attendance processed for {target_date}", "records_updated": result}
