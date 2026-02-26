from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class LocationMaster(Base):
    __tablename__ = "location_master"
    location_id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Integer, nullable=False, default=100)

class EmployeeMaster(Base):
    __tablename__ = "employee_master"
    employee_id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(20), nullable=False, unique=True)
    employee_name = Column(String(150), nullable=False)
    assigned_location_id = Column(Integer, ForeignKey("location_master.location_id"))
    is_valid = Column(Boolean, default=True)

class ClockLogs(Base):
    __tablename__ = "clock_logs"
    log_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee_master.employee_id"), nullable=False)
    punch_timestamp = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    punch_status = Column(String(10))
    is_valid = Column(Boolean) 
    location_status = Column(String(20)) # <--- NEW COLUMN
    device_identifier = Column(String(100))
    address = Column(Text)

class DailyAttendance(Base):
    __tablename__ = "daily_attendance"
    attendance_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee_master.employee_id"), nullable=False)
    attendance_date = Column(Date, nullable=False)
    login_time = Column(DateTime)
    logout_time = Column(DateTime)
    total_working_hours = Column(Float)
    is_valid = Column(Boolean)
    location_status = Column(String(20)) # <--- NEW COLUMN
    created_at = Column(DateTime, default=datetime.utcnow)
