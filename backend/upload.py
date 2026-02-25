from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import services

router = APIRouter()

@router.post("/upload")
async def upload_clock_logs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are allowed.")
    
    result = await services.process_csv_upload(file, db)
    return {"message": "File processed successfully", "data": result}
