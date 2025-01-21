from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import Error
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import date

# fill .env file with your credentials
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password_here
# DB_NAME=Job2main  
load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        print("Attempting database connection...")
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        print("Database connection successful!")
        return connection
    except Error as e:
        print(f"Database connection failed: {e}")
        return None

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/test')
def test_connection():
    conn = get_db_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor(dictionary=True)
        
        # Get all table names
        cursor.execute("SHOW TABLES")
        tables_raw = cursor.fetchall()
        
        # Store data from each table
        data = {}
        for table_dict in tables_raw:
            # Get the first (and only) value from the dictionary
            table_name = list(table_dict.values())[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            data[table_name] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Database connection successful!",
            "data": data
        })
    
    return jsonify({"message": "Database connection failed!"}), 500

#  Employer Endpoints 

# Company Management
@app.route('/api/employers/<int:employer_id>/companies', methods=['POST'])
def create_company(employer_id):
    # Get data from request
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"error": "Company name is required"}), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the employer_id exists in Employer table
            cursor.execute("SELECT UserID FROM Employer WHERE UserID = %s", (employer_id,))
            employer = cursor.fetchone()
            
            if not employer:
                return jsonify({
                    "error": "Invalid employer ID. The user must be an employer to create a company."
                }), 400
            
            # Get the maximum CompanyID to determine the next ID
            cursor.execute("SELECT MAX(CompanyID) as max_id FROM Company")
            result = cursor.fetchone()
            next_id = 1 if result['max_id'] is None else result['max_id'] + 1
            
            # Insert new company with columns specified in correct order
            query = "INSERT INTO Company (CompanyID, CreatedBy, Name, Location) VALUES (%s, %s, %s, %s)"
            values = (
                next_id,  # Use the next available ID
                employer_id,  # employer ID from URL parameter
                data['name'],
                data.get('location', 'TBD')  # location is optional
            )
            
            cursor.execute(query, values)
            
            # Insert a new row in the Employer table for this company
            cursor.execute("""
                INSERT INTO Employer (Company, UserID) 
                VALUES (%s, %s)
            """, (next_id, employer_id))
            
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Company created successfully",
                "company_id": next_id
            }), 201
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/employers/company/<int:company_id>', methods=['PUT'])
def join_company(company_id):
    # Get data from request
    data = request.json
    if not data or 'employer_id' not in data:
        return jsonify({"error": "Employer ID is required"}), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the employer exists
            cursor.execute("SELECT UserID FROM Employer WHERE UserID = %s", (data['employer_id'],))
            employer = cursor.fetchone()
            
            if not employer:
                return jsonify({
                    "error": "Invalid employer ID"
                }), 400
            
            # Verify if the company exists
            cursor.execute("SELECT CompanyID, Name FROM Company WHERE CompanyID = %s", (company_id,))
            company = cursor.fetchone()
            
            if not company:
                return jsonify({
                    "error": "Company not found"
                }), 404
            
            # Check if employer is already in this company
            cursor.execute("""
                SELECT * FROM Employer  
                WHERE UserID = %s AND Company = %s
            """, (data['employer_id'], company_id))
            
            if cursor.fetchone():
                return jsonify({
                    "error": "Employer is already part of this company"
                }), 400
            
            # Insert new row in Employer table
            cursor.execute("""
                INSERT INTO Employer (Company, UserID) 
                VALUES (%s, %s)
            """, (company_id, data['employer_id']))
            
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": f"Successfully joined company {company['Name']}"
            })
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/employers/<int:employer_id>/company', methods=['PUT'])
def quit_company(employer_id):
    # Get data from request
    data = request.json
    if not data or 'company_id' not in data:
        return jsonify({"error": "Company ID is required"}), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the employer exists and has this specific company
            cursor.execute("""
                SELECT e.UserID, e.Company, c.Name as CompanyName, c.CreatedBy
                FROM Employer e, Company c
                WHERE e.Company = c.CompanyID 
                AND e.UserID = %s 
                AND e.Company = %s
            """, (employer_id, data['company_id']))
            employer = cursor.fetchone()
            
            if not employer:
                return jsonify({
                    "error": "Invalid employer ID or employer is not part of this company"
                }), 400
            
            # Update the employer's company to NULL
            cursor.execute("""
                UPDATE Employer 
                SET Company = NULL 
                WHERE UserID = %s AND Company = %s
            """, (employer_id, data['company_id']))
            
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": f"Successfully left company {employer['CompanyName']}"
            })
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/companies/<int:company_id>/locations', methods=['POST'])
def add_location(company_id):
    # Get data from request
    data = request.json
    if not data or 'street' not in data or 'number' not in data or 'city' not in data:
        return jsonify({
            "error": "Street, number, and city are required"
        }), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the company exists
            cursor.execute("SELECT CompanyID FROM Company WHERE CompanyID = %s", (company_id,))
            company = cursor.fetchone()
            
            if not company:
                return jsonify({
                    "error": "Company not found"
                }), 404
            
            # Get the maximum LocationID to determine the next ID
            cursor.execute("SELECT MAX(LocationID) as max_id FROM Location")
            result = cursor.fetchone()
            next_id = 1 if result['max_id'] is None else result['max_id'] + 1
            
            # Insert new location
            query = "INSERT INTO Location (LocationID, Company, Street, Number, City) VALUES (%s, %s, %s, %s, %s)"
            values = (
                next_id,
                company_id,
                data['street'],
                data['number'],
                data['city']
            )
            
            cursor.execute(query, values)
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Location added successfully",
                "location_id": next_id
            }), 201
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/companies/<int:company_id>/locations', methods=['DELETE'])
def delete_location(company_id):
    # Get data from request
    data = request.json
    if not data or 'location_id' not in data:
        return jsonify({"error": "Location ID is required"}), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the location exists and belongs to the company
            cursor.execute("""
                SELECT LocationID, Company 
                FROM Location 
                WHERE LocationID = %s AND Company = %s
            """, (data['location_id'], company_id))
            location = cursor.fetchone()
            
            if not location:
                return jsonify({
                    "error": "Location not found or doesn't belong to this company"
                }), 404
            
            # Check if this is the company's only location
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM Location 
                WHERE Company = %s
            """, (company_id,))
            location_count = cursor.fetchone()['count']
            
            if location_count <= 1:
                return jsonify({
                    "error": "Cannot delete the only location of a company. Company must have at least one location."
                }), 400
            
            # Check if there are any job offers for this location
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM JobOffer 
                WHERE Location = %s
            """, (data['location_id'],))
            joboffer_count = cursor.fetchone()['count']
            
            if joboffer_count > 0:
                return jsonify({
                    "error": "Cannot delete location with active job offers. Please delete the job offers first."
                }), 400
            
            # If all checks pass, delete the location
            cursor.execute("DELETE FROM Location WHERE LocationID = %s", (data['location_id'],))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Location deleted successfully"
            })
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

# Job Management
@app.route('/api/employers/<int:employer_id>/joboffers', methods=['POST'])
def create_job_offer(employer_id):
    # Get data from request
    data = request.json
    if not data or 'location_id' not in data or 'date' not in data or \
       'start_time' not in data or 'end_time' not in data or \
       'max_wage' not in data or 'working_days' not in data or \
       'hours' not in data:
        return jsonify({
            "error": "Required fields: location_id, date, start_time, end_time, max_wage, working_days, hours"
        }), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the employer exists
            cursor.execute("""
                SELECT e.UserID, e.Company 
                FROM Employer e
                WHERE e.UserID = %s
            """, (employer_id,))
            employer = cursor.fetchall()  # Fetch ALL results
            
            if not employer:
                return jsonify({
                    "error": "Invalid employer ID"
                }), 404
            
            # Verify if the location exists and belongs to employer's company
            cursor.execute("""
                SELECT LocationID, Company 
                FROM Location 
                WHERE LocationID = %s AND Company = %s
            """, (data['location_id'], employer[0]['Company']))
            location = cursor.fetchall()  # Fetch ALL results
            
            if not location:
                return jsonify({
                    "error": "Location not found or doesn't belong to your company"
                }), 404
            
            # Get the maximum JobOfferID to determine the next ID
            cursor.execute("SELECT MAX(JobOfferID) as max_id FROM JobOffer")
            result = cursor.fetchall()  # Fetch ALL results
            next_id = 1 if result[0]['max_id'] is None else result[0]['max_id'] + 1
            
            # Insert new job offer
            query = """
                INSERT INTO JobOffer (
                    JobOfferID, Location, CreatedBy, Status, Date, 
                    StartTime, EndTime, MaxWage, WorkingDays, Hours
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                next_id,
                data['location_id'],
                employer_id,  # CreatedBy from URL parameter
                'Open',      # Default status
                data['date'],
                data['start_time'],
                data['end_time'],
                data['max_wage'],
                data['working_days'],
                data['hours']
            )
            
            cursor.execute(query, values)
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Job offer created successfully",
                "job_offer_id": next_id
            }), 201
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/employers/<int:employer_id>/joboffers', methods=['GET'])
def get_my_job_offers(employer_id):
    # Optional status filter from query parameters
    status = request.args.get('status')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the employer exists
            cursor.execute("""
                SELECT UserID FROM Employer 
                WHERE UserID = %s
            """, (employer_id,))
            employer = cursor.fetchall()
            
            if not employer:
                return jsonify({
                    "error": "Invalid employer ID"
                }), 404
            
            # Base query with joins to get location and company info
            base_query = """
                SELECT 
                    j.JobOfferID,
                    j.Location,
                    j.Status,
                    j.Date,
                    j.StartTime,
                    j.EndTime,
                    j.MaxWage,
                    j.WorkingDays,
                    j.Hours,
                    l.Street,
                    l.Number,
                    l.City,
                    c.Name as CompanyName
                FROM JobOffer j, Location l, Company c
                WHERE j.Location = l.LocationID
                  AND l.Company = c.CompanyID
                  AND j.CreatedBy = %s
            """
            
            # Add status filter if provided
            if status:
                base_query += " AND j.Status = %s"
                cursor.execute(base_query, (employer_id, status))
            else:
                cursor.execute(base_query, (employer_id,))
            
            job_offers = cursor.fetchall()
            
            # Convert datetime/timedelta objects to strings
            for job in job_offers:
                if job.get('Date'):
                    job['Date'] = job['Date'].strftime('%Y-%m-%d')
                if job.get('StartTime'):
                    # Convert timedelta to string in HH:MM:SS format
                    total_seconds = int(job['StartTime'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    job['StartTime'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                if job.get('EndTime'):
                    # Convert timedelta to string in HH:MM:SS format
                    total_seconds = int(job['EndTime'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    job['EndTime'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Job offers retrieved successfully",
                "job_offers": job_offers
            })
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

# Application Management
@app.route('/api/applications/status', methods=['PUT'])
def update_application_status():
    # Get data from request
    data = request.json
    if not data or 'new_status' not in data or 'job_offer_id' not in data or 'worker_id' not in data:
        return jsonify({
            "error": "Required fields: new_status, job_offer_id, worker_id"
        }), 400
        
    # Validate status value
    valid_statuses = ['Accepted', 'Refused']
    if data['new_status'] not in valid_statuses:
        return jsonify({
            "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the application exists
            cursor.execute("""
                SELECT a.JobOfferID, a.WorkerID, a.Status, j.Status as JobStatus
                FROM Application a, JobOffer j
                WHERE a.JobOfferID = j.JobOfferID
                  AND a.JobOfferID = %s AND a.WorkerID = %s
            """, (data['job_offer_id'], data['worker_id']))
            application = cursor.fetchone()
            
            if not application:
                return jsonify({
                    "error": "Application not found"
                }), 404
            
            # Check if application is already processed
            if application['Status'] in ['Accepted', 'Refused']:
                return jsonify({
                    "error": f"Application is already {application['Status'].lower()}"
                }), 400
            
            # Check if job offer is still open
            if application['JobStatus'] != 'Open':
                return jsonify({
                    "error": "Cannot update application status: Job offer is no longer open"
                }), 400
            
            # Update application status
            cursor.execute("""
                UPDATE Application 
                SET Status = %s 
                WHERE JobOfferID = %s AND WorkerID = %s
            """, (data['new_status'], data['job_offer_id'], data['worker_id']))
            
            # If accepting the application, close the job offer
            if data['new_status'] == 'Accepted':
                cursor.execute("""
                    UPDATE JobOffer 
                    SET Status = 'Completed' 
                    WHERE JobOfferID = %s
                """, (data['job_offer_id'],))
                
                # Refuse all other pending applications for this job offer
                cursor.execute("""
                    UPDATE Application 
                    SET Status = 'Refused' 
                    WHERE JobOfferID = %s 
                    AND WorkerID != %s 
                    AND Status = 'Pending'
                """, (data['job_offer_id'], data['worker_id']))
            
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": f"Application status updated to {data['new_status']}"
            })
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/workers', methods=['GET'])
def get_all_workers():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    if conn:
        try:
            # Create cursor with dictionary=True to get results as dictionaries
            cursor = conn.cursor(dictionary=True)
            
            # Execute SQL query to get all workers
            cursor.execute("""
                SELECT U.UserID, U.FirstName, U.Surname, U.Name, U.Email, U.PhoneNumber, W.Experiences, W.Description 
                FROM User as U, Worker as W
                WHERE U.UserID = W.UserID
            """)
            
            # Fetch all results
            workers = cursor.fetchall()
            
            # Clean up
            cursor.close()
            conn.close()
            
            # Return results as JSON
            return jsonify({"workers": workers})
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

#  Worker Endpoints 

@app.route('/api/joboffers/available', methods=['GET'])
def get_available_jobs():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT J.JobOfferID, J.Location, J.Date, J.StartTime, J.EndTime, J.MaxWage, J.WorkingDays, J.Hours, L.Street, L.Number, L.City, C.Name as CompanyName
                FROM JobOffer as J, Location as L, Company as C
                WHERE J.Location = L.LocationID
                  AND L.Company = C.CompanyID
                  AND J.Status = 'Open'
                ORDER BY J.Date ASC
            """)
            
            jobs = cursor.fetchall()
            
            # Convert datetime/timedelta objects to strings
            for job in jobs:
                if job.get('Date'):
                    job['Date'] = job['Date'].strftime('%Y-%m-%d')
                if job.get('StartTime'):
                    # Convert timedelta to string in HH:MM:SS format
                    total_seconds = int(job['StartTime'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    job['StartTime'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                if job.get('EndTime'):
                    # Convert timedelta to string in HH:MM:SS format
                    total_seconds = int(job['EndTime'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    job['EndTime'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Available jobs retrieved successfully",
                "jobs": jobs
            })
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/joboffers/<int:job_id>/apply', methods=['POST'])
def apply_to_job(job_id):
    # Get data from request
    data = request.json
    if not data or 'worker_id' not in data or 'wage_offer' not in data:
        return jsonify({
            "error": "Required fields: worker_id, wage_offer"
        }), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the job offer exists and is open
            cursor.execute("""
                SELECT JobOfferID, Status, MaxWage 
                FROM JobOffer 
                WHERE JobOfferID = %s
            """, (job_id,))
            job_offer = cursor.fetchone()
            
            if not job_offer:
                return jsonify({
                    "error": "Job offer not found"
                }), 404
                
            if job_offer['Status'] != 'Open':
                return jsonify({
                    "error": "This job offer is no longer open for applications"
                }), 400
            
            # Verify if the worker exists
            cursor.execute("""
                SELECT UserID 
                FROM Worker 
                WHERE UserID = %s
            """, (data['worker_id'],))
            worker = cursor.fetchone()
            
            if not worker:
                return jsonify({
                    "error": "Invalid worker ID"
                }), 404
            
            # Check if wage offer is not higher than maximum wage
            if float(data['wage_offer']) > float(job_offer['MaxWage']):
                return jsonify({
                    "error": f"Wage offer cannot be higher than maximum wage ({job_offer['MaxWage']})"
                }), 400
            
            # Check if worker has already applied to this job offer
            cursor.execute("""
                SELECT Status 
                FROM Application 
                WHERE JobOfferID = %s AND WorkerID = %s
            """, (job_id, data['worker_id']))
            existing_application = cursor.fetchone()
            
            if existing_application:
                return jsonify({
                    "error": "You have already applied to this job offer"
                }), 400
            
            # Get current date in YYYY-MM-DD format
            current_date = date.today().strftime('%Y-%m-%d')
            
            # Create the application with current date
            cursor.execute("""
                INSERT INTO Application (JobOfferID, WorkerID, Status, WageOffer, Date) 
                VALUES (%s, %s, %s, %s, %s)
            """, (job_id, data['worker_id'], 'PENDING', data['wage_offer'], current_date))
            
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Application submitted successfully",
                "application_date": current_date
            }), 201
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/workers/<int:worker_id>/applications', methods=['GET'])
def get_my_applications(worker_id):
    # Optional status filter from query parameters
    status = request.args.get('status')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the worker exists
            cursor.execute("""
                SELECT UserID 
                FROM Worker 
                WHERE UserID = %s
            """, (worker_id,))
            worker = cursor.fetchone()
            
            if not worker:
                return jsonify({
                    "error": "Invalid worker ID"
                }), 404
            
            # Base query with joins to get job offer, location and company info
            base_query = """
                SELECT 
                    a.JobOfferID,
                    a.WorkerID,
                    a.Status as ApplicationStatus,
                    a.WageOffer,
                    a.Date as ApplicationDate,
                    j.Status as JobStatus,
                    j.Date as JobDate,
                    j.StartTime,
                    j.EndTime,
                    j.MaxWage,
                    j.WorkingDays,
                    j.Hours,
                    l.Street,
                    l.Number,
                    l.City,
                    c.Name as CompanyName
                FROM Application a, JobOffer j, Location l, Company c
                WHERE a.JobOfferID = j.JobOfferID
                  AND j.Location = l.LocationID
                  AND l.Company = c.CompanyID
                  AND a.WorkerID = %s
            """
            
            # Add status filter if provided
            if status:
                base_query += " AND a.Status = %s"
                cursor.execute(base_query, (worker_id, status))
            else:
                cursor.execute(base_query, (worker_id,))
            
            applications = cursor.fetchall()
            
            # Convert datetime/timedelta objects to strings
            for app in applications:
                if app.get('ApplicationDate'):
                    app['ApplicationDate'] = app['ApplicationDate'].strftime('%Y-%m-%d')
                if app.get('JobDate'):
                    app['JobDate'] = app['JobDate'].strftime('%Y-%m-%d')
                if app.get('StartTime'):
                    # Convert timedelta to string in HH:MM:SS format
                    total_seconds = int(app['StartTime'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    app['StartTime'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                if app.get('EndTime'):
                    # Convert timedelta to string in HH:MM:SS format
                    total_seconds = int(app['EndTime'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    app['EndTime'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Applications retrieved successfully",
                "applications": applications
            })
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/joboffers/<int:job_id>/employer', methods=['GET'])
def get_job_employer_info(job_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get job offer with employer and company information
            cursor.execute("""
                SELECT 
                    j.JobOfferID,
                    j.CreatedBy as EmployerID,
                    u.FirstName,
                    u.Surname,
                    u.Email,
                    u.PhoneNumber,
                    c.CompanyID,
                    c.Name as CompanyName,
                    l.Street,
                    l.Number,
                    l.City
                FROM JobOffer j, User u, Location l, Company c
                WHERE j.CreatedBy = u.UserID
                  AND j.Location = l.LocationID
                  AND l.Company = c.CompanyID
                  AND j.JobOfferID = %s
            """, (job_id,))
            
            result = cursor.fetchone()
            
            if not result:
                return jsonify({
                    "error": "Job offer not found"
                }), 404
            
            # Structure the response
            response = {
                "employer": {
                    "id": result['EmployerID'],
                    "first_name": result['FirstName'],
                    "surname": result['Surname'],
                    "email": result['Email'],
                    "phone_number": result['PhoneNumber']
                },
                "company": {
                    "id": result['CompanyID'],
                    "name": result['CompanyName'],
                    "location": {
                        "street": result['Street'],
                        "number": result['Number'],
                        "city": result['City']
                    }
                }
            }
            
            cursor.close()
            conn.close()
            
            return jsonify(response)
            
        except Error as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Database connection failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=4000)
