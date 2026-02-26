from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from database import get_db
import services

router = APIRouter()

@router.get("/reports/daily")
def get_daily_report(target_date: str, db: Session = Depends(get_db)):
    csv_data = services.fetch_daily_report_csv(target_date, db)
    return Response(
        content=csv_data, 
        media_type="text/csv", 
        headers={"Content-Disposition": f"attachment; filename=Daily_Attendance_{target_date}.csv"}
    )

@router.get("/reports/monthly")
def get_monthly_summary(month: int, year: int, db: Session = Depends(get_db)):
    csv_data = services.fetch_monthly_summary_csv(month, year, db)
    return Response(
        content=csv_data, 
        media_type="text/csv", 
        headers={"Content-Disposition": f"attachment; filename=Monthly_Summary_{month}_{year}.csv"}
    )
