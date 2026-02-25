CREATE TABLE employee_master (
    employee_id SERIAL PRIMARY KEY,
    employee_code VARCHAR(20) NOT NULL UNIQUE,
    employee_name VARCHAR(150) NOT NULL,
    client_mapping VARCHAR(150),
    work_mode VARCHAR(20),
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clock_logs (
    log_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employee_master(employee_id),
    punch_timestamp TIMESTAMP NOT NULL,
    location_name VARCHAR(150),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    punch_status VARCHAR(10),
    device_identifier VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE daily_attendance (
    attendance_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employee_master(employee_id),
    attendance_date DATE NOT NULL,
    login_time TIMESTAMP,
    logout_time TIMESTAMP,
    total_working_hours DECIMAL(5,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
