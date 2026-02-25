from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import services

router = APIRouter()

@router.get("/reports/daily")
def get_daily_report(target_date: str, db: Session = Depends(get_db)):
    data = services.fetch_daily_report(target_date, db)
    return data

@router.get("/reports/monthly")
def get_monthly_summary(month: int, year: int, db: Session = Depends(get_db)):
    data = services.fetch_monthly_summary(month, year, db)
    return data
