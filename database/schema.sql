-- 1. Create Location Master for dynamic geofencing
CREATE TABLE location_master (
    location_id SERIAL PRIMARY KEY,
    location_name VARCHAR(150) NOT NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    radius INTEGER NOT NULL DEFAULT 100
);

-- 2. Employee Master now links to a location and uses boolean status
CREATE TABLE employee_master (
    employee_id SERIAL PRIMARY KEY,
    employee_code VARCHAR(20) NOT NULL UNIQUE,
    employee_name VARCHAR(150) NOT NULL,
    assigned_location_id INTEGER REFERENCES location_master(location_id),
    is_valid BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Clock Logs
CREATE TABLE clock_logs (
    log_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employee_master(employee_id),
    punch_timestamp TIMESTAMP NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    punch_status VARCHAR(10),
    is_valid BOOLEAN, -- Geofence check result
    device_identifier VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Daily Attendance
CREATE TABLE daily_attendance (
    attendance_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employee_master(employee_id),
    attendance_date DATE NOT NULL,
    login_time TIMESTAMP,
    logout_time TIMESTAMP,
    total_working_hours DECIMAL(5,2),
    is_valid BOOLEAN, -- Validates if attendance met criteria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Monthly Summary
CREATE TABLE monthly_summary (
    summary_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employee_master(employee_id),
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    office_days INTEGER DEFAULT 0,
    remote_days INTEGER DEFAULT 0,
    total_days_present INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INSERT A DEFAULT OFFICE LOCATION FOR TESTING
INSERT INTO location_master (location_name, latitude, longitude, radius) 
VALUES ('Headquarters', 19.0760, 72.8777, 100);
