# Import FastAPI framework
from fastapi import FastAPI

# Import CORS middleware (used to allow frontend-backend communication)
from fastapi.middleware.cors import CORSMiddleware

# Import models (this ensures table classes are registered with SQLAlchemy Base)
import models

# Import engine to connect and create tables
from database import engine

# Import different route modules (feature-based separation)
import upload, attendance, reports


# ------------------------------------------------
# CREATE DATABASE TABLES (IF NOT ALREADY CREATED)
# ------------------------------------------------
# This command tells SQLAlchemy:
# "Create all tables defined in models.py"
# It checks if tables exist — if not, it creates them.
models.Base.metadata.create_all(bind=engine)


# ------------------------------------------------
# CREATE FASTAPI APPLICATION INSTANCE
# ------------------------------------------------
# Title will appear in Swagger documentation (/docs)
app = FastAPI(title="Smart Attendance Platform API")


# ------------------------------------------------
# ENABLE CORS (Cross-Origin Resource Sharing)
# ------------------------------------------------
# This allows frontend apps (React, Angular, etc.)
# to communicate with this backend API.
# allow_origins=["*"] means allow all domains (development mode).
# In production, you should restrict this to specific domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins
    allow_credentials=True,    # Allow cookies/auth headers
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],       # Allow all headers
)


# ------------------------------------------------
# INCLUDE ROUTERS (MODULAR API STRUCTURE)
# ------------------------------------------------
# This connects different feature modules to the main app.

# Upload-related APIs → accessible at /api/...
app.include_router(upload.router, prefix="/api", tags=["Upload"])

# Attendance processing APIs → accessible at /api/...
app.include_router(attendance.router, prefix="/api", tags=["Attendance"])

# Reports APIs → accessible at /api/...
app.include_router(reports.router, prefix="/api", tags=["Reports"])


# ------------------------------------------------
# HEALTH CHECK ENDPOINT
# ------------------------------------------------
# Simple endpoint to verify that API is running.
# Visit: http://localhost:8000/
@app.get("/")
def health_check():
    return {"status": "API is running securely!"}
