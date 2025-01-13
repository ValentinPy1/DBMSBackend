from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import Error
import mysql.connector
import os
from dotenv import load_dotenv

# Fill .env file with your own credentials 
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password_here
# DB_NAME=Job2main
load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        print("Attempting database connection...") # Debug print
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        print("Database connection successful!") # Debug print
        return connection
    except Error as e:
        print(f"Database connection failed: {e}") # Debug print
        return None

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/test')
def test_connection():
    conn = get_db_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({
            "message": "Database connection successful!",
            "tables": tables
        })
    return jsonify({"message": "Database connection failed!"}), 500

#  Employer Endpoints 

# Company Management
@app.route('/api/companies', methods=['POST'])
def create_company():
    # TODO: Create a new company
    # Expected input: company name, location
    return jsonify({"message": "Company created successfully"}), 201

@app.route('/api/employers/company/<int:company_id>', methods=['PUT'])
def join_company(company_id):
    # TODO: Join a company
    # Expected input: employer_id
    return jsonify({"message": "Joined company successfully"})

@app.route('/api/employers/company', methods=['PUT'])
def quit_company():
    # TODO: Quit current company
    # Expected input: employer_id
    return jsonify({"message": "Left company successfully"})

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
    # TODO: Get all workers
    return jsonify({"workers": []})

#  Worker Endpoints 

@app.route('/api/joboffers/available', methods=['GET'])
def get_available_jobs():
    # TODO: Get all available jobs
    return jsonify({"jobs": []})

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
