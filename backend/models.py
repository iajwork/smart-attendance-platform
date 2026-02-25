from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class EmployeeMaster(Base):
    __tablename__ = "employee_master"
    employee_id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(20), nullable=False, unique=True)
    employee_name = Column(String(150), nullable=False)
    client_mapping = Column(String(150))
    work_mode = Column(String(20))
    status = Column(String(20), default="Active")

class ClockLogs(Base):
    __tablename__ = "clock_logs"
    log_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee_master.employee_id"), nullable=False)
    punch_timestamp = Column(DateTime, nullable=False)
    location_name = Column(String(150), nullable=False, default="Unknown")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    punch_status = Column(String(10))
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
    status = Column(String(20)) 
    created_at = Column(DateTime, default=datetime.utcnow)

class MonthlySummary(Base):
    __tablename__ = "monthly_summary"
    summary_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee_master.employee_id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    office_days = Column(Integer, default=0)
    remote_days = Column(Integer, default=0)
    total_days_present = Column(Integer, default=0)
