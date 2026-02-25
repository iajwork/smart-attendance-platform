import pandas as pd
from sqlalchemy.orm import Session
from datetime import date
import io
import models
import utils

async def process_csv_upload(file, db: Session):
    contents = await file.read()
    file_stream = io.BytesIO(contents)
    
    if file.filename.endswith('.csv'):
        raw_df = pd.read_csv(file_stream, header=None)
    else:
        raw_df = pd.read_excel(file_stream, header=None)

    header_row = None
    for i in range(15):
        if i >= len(raw_df): break
        row_values = raw_df.iloc[i].fillna("").astype(str).str.lower().tolist()
        joined_row = " ".join(str(x) for x in row_values)
        if "employee number" in joined_row:
            header_row = i
            break
            
    if header_row is None:
        raise Exception("Could not find 'Employee Number' column.")
        
    file_stream.seek(0)
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file_stream, header=header_row)
    else:
        df = pd.read_excel(file_stream, header=header_row)
        
    df.columns = df.columns.astype(str).str.strip().str.lower()
    
    column_map = {
        "employee number": "employee_code",
        "employee name": "employee_name",
        "time stamp": "punch_timestamp",
        "punch status": "punch_status",
        "device identifier": "device_identifier",
        "latitude": "latitude",
        "longitude": "longitude",
        "address": "address"
    }
    df = df.rename(columns=column_map)

    df["employee_code"] = df["employee_code"].astype(str).str.strip().str.upper()
    df["punch_timestamp"] = pd.to_datetime(df["punch_timestamp"], errors='coerce')
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=['punch_timestamp', 'employee_code'])

    unique_employees = df[["employee_code", "employee_name"]].drop_duplicates(subset=['employee_code'])
    for _, row in unique_employees.iterrows():
        existing = db.query(models.EmployeeMaster).filter_by(employee_code=row['employee_code']).first()
        if not existing:
            new_emp = models.EmployeeMaster(
                employee_code=row['employee_code'], 
                employee_name=row['employee_name']
            )
            db.add(new_emp)
    db.commit()

    employees_in_db = db.query(models.EmployeeMaster).all()
    emp_map = {emp.employee_code: emp.employee_id for emp in employees_in_db}
    
    records_inserted = 0
    for _, row in df.iterrows():
        emp_id = emp_map.get(row['employee_code'])
        if emp_id:
            log_entry = models.ClockLogs(
                employee_id=emp_id,
                punch_timestamp=row['punch_timestamp'],
                location_name="Unknown",
                latitude=row['latitude'],
                longitude=row['longitude'],
                punch_status=row.get('punch_status'),
                device_identifier=row.get('device_identifier'),
                address=row.get('address')
            )
            db.add(log_entry)
            records_inserted += 1
            
    db.commit()
    return {"status": "success", "records_processed": records_inserted}


def calculate_daily_attendance(target_date: date, db: Session):
    start_of_day = pd.to_datetime(target_date)
    end_of_day = start_of_day + pd.Timedelta(days=1)
    
    logs = db.query(models.ClockLogs).filter(
        models.ClockLogs.punch_timestamp >= start_of_day,
        models.ClockLogs.punch_timestamp < end_of_day
    ).all()
    
    if not logs: return 0
        
    df_logs = pd.DataFrame([{
        'employee_id': log.employee_id,
        'punch_timestamp': log.punch_timestamp,
        'lat': log.latitude,
        'lon': log.longitude
    } for log in logs])
    
    grouped = df_logs.groupby('employee_id')
    records_updated = 0
    
    for emp_id, group in grouped:
        first_punch = group['punch_timestamp'].min()
        last_punch = group['punch_timestamp'].max()
        duration = (last_punch - first_punch).total_seconds() / 3600 if first_punch != last_punch else 0
        
        first_log = group.loc[group['punch_timestamp'].idxmin()]
        geo_status = utils.get_attendance_status(first_log['lat'], first_log['lon'])
        
        attendance_status = "Present" if duration > 4 else "Half-day" if duration > 0 else "Absent"
        if geo_status == "REMOTE": attendance_status = "Remote"
            
        existing_record = db.query(models.DailyAttendance).filter_by(employee_id=emp_id, attendance_date=target_date).first()
        if existing_record:
            existing_record.login_time = first_punch
            existing_record.logout_time = last_punch
            existing_record.total_working_hours = round(duration, 2)
            existing_record.status = attendance_status
        else:
            new_record = models.DailyAttendance(
                employee_id=emp_id, attendance_date=target_date,
                login_time=first_punch, logout_time=last_punch,
                total_working_hours=round(duration, 2), status=attendance_status
            )
            db.add(new_record)
        records_updated += 1
        
    db.commit()
    return records_updated


def fetch_daily_report(target_date: str, db: Session):
    records = db.query(models.DailyAttendance, models.EmployeeMaster).join(
        models.EmployeeMaster, models.DailyAttendance.employee_id == models.EmployeeMaster.employee_id
    ).filter(models.DailyAttendance.attendance_date == target_date).all()
    
    rows = []
    for att, emp in records:
        rows.append({
            "Employee Code": emp.employee_code,
            "Employee Name": emp.employee_name,
            "In Time": att.login_time.strftime("%H:%M") if att.login_time else "-",
            "Out Time": att.logout_time.strftime("%H:%M") if att.logout_time else "-",
            "Hours": f"{att.total_working_hours} hrs" if att.total_working_hours else "-",
            "Status": att.status
        })
    
    return {
        "title": "Daily Attendance Snapshot",
        "subtitle": f"Workforce statistics for {target_date}",
        "dateStr": target_date,
        "columns": ["Employee Code", "Employee Name", "In Time", "Out Time", "Hours", "Status"],
        "rows": rows
    }

def fetch_monthly_summary(month: int, year: int, db: Session):
    # Logic for month rollup would go here, returning placeholder format for UI:
    return {
         "title": "Monthly Attendance Rollup",
         "subtitle": f"Summary for {month}/{year}",
         "dateStr": f"{year}-{month:02d}",
         "columns": ["Employee Code", "Employee Name", "Office Days", "Remote Days", "Total Days"],
         "rows": [] # Add Monthly Summary querying here
    }
