from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import Error
import mysql.connector
import os
from dotenv import load_dotenv

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
@app.route('/api/companies', methods=['POST'])
def create_company():
    # Get data from request
    data = request.json
    if not data or 'name' not in data or 'createdBy' not in data:
        return jsonify({"error": "Company name and creator ID (createdBy) are required"}), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the createdBy ID exists in Employer table
            cursor.execute("SELECT UserID FROM Employer WHERE UserID = %s", (data['createdBy'],))
            employer = cursor.fetchone()
            
            if not employer:
                return jsonify({
                    "error": "Invalid creator ID. The user must be an employer to create a company."
                }), 400
            
            # Get the maximum CompanyID to determine the next ID
            cursor.execute("SELECT MAX(CompanyID) as max_id FROM Company")
            result = cursor.fetchone()
            next_id = 1 if result['max_id'] is None else result['max_id'] + 1
            
            # Insert new company with columns specified in correct order
            query = "INSERT INTO Company (CompanyID, CreatedBy, Name, Location) VALUES (%s, %s, %s, %s)"
            values = (
                next_id,  # Use the next available ID
                data['createdBy'],  # employer ID who creates the company
                data['name'],
                data.get('location', 'TBD')  # location is optional
            )
            
            cursor.execute(query, values)
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
    # TODO: Join a company
    # Expected input: employer_id
    return jsonify({"message": "Joined company successfully"})

@app.route('/api/employers/company', methods=['PUT'])
def quit_company():
    # Get data from request
    data = request.json
    if not data or 'employer_id' not in data:
        return jsonify({"error": "Employer ID is required"}), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First verify if the employer exists and has a company
            cursor.execute("""
                SELECT e.UserID, e.Company, c.Name as CompanyName 
                FROM Employer e, Company c
                WHERE e.Company = c.CompanyID AND e.UserID = %s
            """, (data['employer_id'],))
            employer = cursor.fetchone()
            
            if not employer:
                return jsonify({
                    "error": "Invalid employer ID"
                }), 400
                
            if not employer['Company']:
                return jsonify({
                    "error": "Employer is not part of any company"
                }), 400
            
            # Update employer's company to NULL
            cursor.execute("""
                UPDATE Employer 
                SET Company = NULL 
                WHERE UserID = %s
            """, (data['employer_id'],))
            
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
    # TODO: Add new location
    # Expected input: street, number, city
    return jsonify({"message": "Location added successfully"}), 201

@app.route('/api/companies/<int:company_id>/locations/<int:location_id>', methods=['DELETE'])
def delete_location(company_id, location_id):
    # TODO: Delete location
    return jsonify({"message": "Location deleted successfully"})

# Job Management
@app.route('/api/joboffers', methods=['POST'])
def create_job_offer():
    # TODO: Create new job offer
    # Expected input: location_id, date, start_time, end_time, max_wage, working_days, hours
    return jsonify({"message": "Job offer created successfully"}), 201

@app.route('/api/employers/joboffers', methods=['GET'])
def get_my_job_offers():
    # TODO: Get job offers for employer
    # Optional query param: status
    status = request.args.get('status')
    return jsonify({"job_offers": []})

# Application Management
@app.route('/api/applications/<int:application_id>/status', methods=['PUT'])
def update_application_status(application_id):
    # TODO: Update application status (refused/accepted)
    # Expected input: new_status
    return jsonify({"message": "Application status updated successfully"})

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
    # TODO: Create job application
    # Expected input: worker_id, wage_offer
    return jsonify({"message": "Application submitted successfully"}), 201

@app.route('/api/workers/applications', methods=['GET'])
def get_my_applications():
    # TODO: Get worker's applications
    # Optional query param: status
    status = request.args.get('status')
    return jsonify({"applications": []})

@app.route('/api/joboffers/<int:job_id>/employer', methods=['GET'])
def get_job_employer_info(job_id):
    # TODO: Get employer and company info for job
    return jsonify({
        "employer": {},
        "company": {}
    })

if __name__ == '__main__':
    app.run(debug=True, port=4000)
