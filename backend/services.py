import pandas as pd
from sqlalchemy.orm import Session
from datetime import date
import io
import models
import utils
import calendar

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

    # Sync Employees
    unique_employees = df[["employee_code", "employee_name"]].drop_duplicates(subset=['employee_code'])
    
    for _, row in unique_employees.iterrows():
        existing = db.query(models.EmployeeMaster).filter_by(employee_code=row['employee_code']).first()
        if not existing:
            new_emp = models.EmployeeMaster(
                employee_code=row['employee_code'], 
                employee_name=row['employee_name'],
                is_valid=True
            )
            db.add(new_emp)
    db.commit()

    # Get employee mapping
    employees_in_db = db.query(models.EmployeeMaster).all()
    emp_map = {emp.employee_code: emp.employee_id for emp in employees_in_db}
    
    # Get all valid office locations from DB
    locations_in_db = db.query(models.LocationMaster).all()
    all_office_locations = [
        {"lat": loc.latitude, "lon": loc.longitude, "radius": loc.radius} 
        for loc in locations_in_db
    ]
    
    records_inserted = 0
    for _, row in df.iterrows():
        emp_id = emp_map.get(row['employee_code'])
        if emp_id:
            # Calculate status using new multi-office logic
            loc_status = utils.get_location_status(
                lat=row['latitude'],
                lon=row['longitude'],
                all_office_locations=all_office_locations
            )
            
            is_valid_punch = (loc_status == "In office")

            log_entry = models.ClockLogs(
                employee_id=emp_id,
                punch_timestamp=row['punch_timestamp'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                punch_status=row.get('punch_status'),
                is_valid=is_valid_punch, 
                location_status=loc_status, 
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
        'is_valid': log.is_valid,
        'location_status': log.location_status 
    } for log in logs])
    
    grouped = df_logs.groupby('employee_id')
    records_updated = 0
    
    for emp_id, group in grouped:
        first_punch = group['punch_timestamp'].min()
        last_punch = group['punch_timestamp'].max()
        duration = (last_punch - first_punch).total_seconds() / 3600 if first_punch != last_punch else 0
        
        first_log = group.loc[group['punch_timestamp'].idxmin()]
        attendance_is_valid = bool(first_log['is_valid'] and duration > 4)
        
        # Check if they forgot to clock out (only 1 punch)
        if first_punch == last_punch:
            daily_loc_status = "invalid"
        else:
            daily_loc_status = first_log['location_status'] 
            
        existing_record = db.query(models.DailyAttendance).filter_by(employee_id=emp_id, attendance_date=target_date).first()
        if existing_record:
            existing_record.login_time = first_punch
            existing_record.logout_time = last_punch
            existing_record.total_working_hours = round(duration, 2)
            existing_record.is_valid = attendance_is_valid
            existing_record.location_status = daily_loc_status
        else:
            new_record = models.DailyAttendance(
                employee_id=emp_id, attendance_date=target_date,
                login_time=first_punch, logout_time=last_punch,
                total_working_hours=round(duration, 2), 
                is_valid=attendance_is_valid,
                location_status=daily_loc_status 
            )
            db.add(new_record)
        records_updated += 1
        
    db.commit()
    return records_updated


def process_entire_month(month: int, year: int, db: Session):
    _, num_days = calendar.monthrange(year, month)
    
    total_records = 0
    days_with_data = 0
    
    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
        records_updated = calculate_daily_attendance(current_date, db)
        
        if records_updated > 0:
            total_records += records_updated
            days_with_data += 1
            
    return {"days_processed": days_with_data, "total_daily_records_created": total_records}


def fetch_daily_report_csv(target_date: str, db: Session):
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
            "Hours": round(att.total_working_hours, 2) if att.total_working_hours else 0,
            "Location": att.location_status 
        })
        
    df = pd.DataFrame(rows)
    return df.to_csv(index=False) 


def fetch_monthly_summary_csv(month: int, year: int, db: Session):
    records = db.query(models.DailyAttendance, models.EmployeeMaster).join(
        models.EmployeeMaster, models.DailyAttendance.employee_id == models.EmployeeMaster.employee_id
    ).all()
    
    summary_dict = {}
    
    for att, emp in records:
        if att.attendance_date.month == int(month) and att.attendance_date.year == int(year):
            emp_code = emp.employee_code
            
            if emp_code not in summary_dict:
                summary_dict[emp_code] = {
                    "employee_id": emp.employee_id,
                    "Employee Code": emp_code,
                    "Employee Name": emp.employee_name,
                    "Office Days": 0,
                    "Remote Days": 0,
                    "Invalid Days": 0,
                    "Total Days": 0
                }
            
            # Tally locations
            if att.location_status == "In office":
                summary_dict[emp_code]["Office Days"] += 1
            elif att.location_status == "REMOTE":
                summary_dict[emp_code]["Remote Days"] += 1
            elif att.location_status == "invalid":
                summary_dict[emp_code]["Invalid Days"] += 1
                
            summary_dict[emp_code]["Total Days"] += 1
            
    # Normalize DB Save
    for emp_code, data in summary_dict.items():
        existing_summary = db.query(models.MonthlySummary).filter_by(
            employee_id=data["employee_id"], month=int(month), year=int(year)
        ).first()
        
        if existing_summary:
            existing_summary.office_days = data["Office Days"]
            existing_summary.remote_days = data["Remote Days"]
            existing_summary.invalid_days = data["Invalid Days"]
            existing_summary.total_days_present = data["Total Days"]
        else:
            new_summary = models.MonthlySummary(
                employee_id=data["employee_id"],
                month=int(month),
                year=int(year),
                office_days=data["Office Days"],
                remote_days=data["Remote Days"],
                invalid_days=data["Invalid Days"],
                total_days_present=data["Total Days"]
            )
            db.add(new_summary)
            
    db.commit()
            
    # Generate CSV Blob
    rows = [
        {k: v for k, v in data.items() if k != "employee_id"} 
        for data in summary_dict.values()
    ]
    
    df = pd.DataFrame(rows, columns=["Employee Code", "Employee Name", "Office Days", "Remote Days", "Invalid Days", "Total Days"])
    return df.to_csv(index=False)
