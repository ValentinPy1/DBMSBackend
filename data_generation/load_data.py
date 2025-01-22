import csv
import mysql.connector
import os

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        # password='your_password_here',
        database='Job2main'
    )

# Function to load CSV data into a table
def load_csv_to_table(file_path, table_name, primary_key):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        columns = reader.fieldnames
        for row in reader:
            # Check if the entry already exists
            check_query = f"SELECT COUNT(*) FROM {table_name} WHERE {primary_key} = %s"
            cursor.execute(check_query, (row[primary_key],))
            if cursor.fetchone()[0] == 0:
                values = [row[col] for col in columns]
                placeholders = ', '.join(['%s'] * len(columns))
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(query, values)
    
    conn.commit()
    cursor.close()
    conn.close()

# Load data into tables
load_csv_to_table('data/User.csv', 'User', 'UserID')
load_csv_to_table('data/Company.csv', 'Company', 'CompanyID')
load_csv_to_table('data/Employer.csv', 'Employer', 'UserID')
load_csv_to_table('data/Worker.csv', 'Worker', 'UserID')
load_csv_to_table('data/Location.csv', 'Location', 'LocationID')
load_csv_to_table('data/JobOffer.csv', 'JobOffer', 'JobOfferID')
load_csv_to_table('data/Application.csv', 'Application', 'WorkerID')

print("Data loaded successfully!")