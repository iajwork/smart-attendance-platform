from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
import upload, attendance, reports

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Attendance Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(attendance.router, prefix="/api", tags=["Attendance"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])

@app.get("/")
def health_check():
    return {"status": "API is running securely!"}
