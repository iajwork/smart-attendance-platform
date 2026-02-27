# Import SQLAlchemy column types and constraints
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text, Boolean

# Used to define relationships between tables (not used yet but available)
from sqlalchemy.orm import relationship

# Base class that all models inherit from (defined in database.py)
from database import Base

# Used to set default timestamps
from datetime import datetime


# ==========================================================
# LOCATION MASTER TABLE
# ==========================================================
# Stores office/location details with geo-coordinates
class LocationMaster(Base):
    __tablename__ = "location_master"  # Table name in database

    location_id = Column(Integer, primary_key=True, index=True)  # Unique ID for location
    location_name = Column(String(150), nullable=False)           # Name of office/location
    latitude = Column(Float, nullable=False)                      # Latitude coordinate
    longitude = Column(Float, nullable=False)                     # Longitude coordinate
    radius = Column(Integer, nullable=False, default=1000)        # Allowed radius (in meters) for geo-fencing


# ==========================================================
# EMPLOYEE MASTER TABLE
# ==========================================================
# Stores employee information
class EmployeeMaster(Base):
    __tablename__ = "employee_master"

    employee_id = Column(Integer, primary_key=True, index=True)     # Unique employee ID
    employee_code = Column(String(20), nullable=False, unique=True) # Unique employee code (like EMP001)
    employee_name = Column(String(150), nullable=False)             # Employee full name
    
    # Foreign key linking employee to assigned office location
    assigned_location_id = Column(Integer, ForeignKey("location_master.location_id"))
    
    is_valid = Column(Boolean, default=True)  # Soft delete flag (True = Active employee)


# ==========================================================
# CLOCK LOGS TABLE
# ==========================================================
# Stores raw punch-in and punch-out logs from device/app
class ClockLogs(Base):
    __tablename__ = "clock_logs"

    log_id = Column(Integer, primary_key=True, index=True)  # Unique log ID

    # Foreign key linking log to employee
    employee_id = Column(Integer, ForeignKey("employee_master.employee_id"), nullable=False)

    punch_timestamp = Column(DateTime, nullable=False)  # Exact punch time
    latitude = Column(Float, nullable=False)            # Punch latitude
    longitude = Column(Float, nullable=False)           # Punch longitude
    
    punch_status = Column(String(10))   # IN / OUT
    is_valid = Column(Boolean)          # Valid punch or rejected
    location_status = Column(String(20))  # Office / Remote / Outside Radius
    
    device_identifier = Column(String(100))  # Device ID (mobile/device tracking)
    address = Column(Text)                   # Human-readable address (optional)


# ==========================================================
# DAILY ATTENDANCE TABLE
# ==========================================================
# Stores processed attendance per employee per day
class DailyAttendance(Base):
    __tablename__ = "daily_attendance"

    attendance_id = Column(Integer, primary_key=True, index=True)  # Unique attendance ID

    # Link to employee
    employee_id = Column(Integer, ForeignKey("employee_master.employee_id"), nullable=False)

    attendance_date = Column(Date, nullable=False)  # Date of attendance

    login_time = Column(DateTime)         # First punch IN
    logout_time = Column(DateTime)        # Last punch OUT
    total_working_hours = Column(Float)   # Calculated working hours

    is_valid = Column(Boolean)            # Whether attendance record is valid
    location_status = Column(String(20))  # Office / Remote (final decision)

    # Automatically store record creation time
    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================================================
# MONTHLY SUMMARY TABLE
# ==========================================================
# Stores aggregated monthly attendance data
class MonthlySummary(Base):
    __tablename__ = "monthly_summary"

    summary_id = Column(Integer, primary_key=True, index=True)  # Unique summary ID

    # Link to employee
    employee_id = Column(Integer, ForeignKey("employee_master.employee_id"), nullable=False)

    month = Column(Integer, nullable=False)  # Month (1-12)
    year = Column(Integer, nullable=False)   # Year (e.g., 2026)

    office_days = Column(Integer, default=0)        # Number of days worked from office
    remote_days = Column(Integer, default=0)        # Number of remote days
    total_days_present = Column(Integer, default=0) # Total present days

    # Automatically store record creation time
    created_at = Column(DateTime, default=datetime.utcnow)
