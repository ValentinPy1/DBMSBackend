import pymysql
import random
from datetime import datetime, timedelta
import uuid

# Database connection
connection = pymysql.connect(
    host='localhost',
    user='root',
    # password='root',
    database='mysql'
)

cursor = connection.cursor()

cursor.execute("USE Job2main")

# generate random data
def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def random_string(length):
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))

def random_phone():
    return ''.join(random.choices('0123456789', k=10))

# User table
users = []
for i in range(10):
    user_id = i
    firstname = random_string(5).capitalize()
    surname = random_string(7).capitalize()
    email = f"{firstname.lower()}.{surname.lower()}@example.com"
    phone = random_phone()
    users.append((i, firstname, surname, email, phone))

cursor.executemany(
    """
    INSERT INTO User (UserID, FirstName, Surname, Email, PhoneNumber)
    VALUES (%s, %s, %s, %s, %s)
    """,
    users
)
connection.commit()

# User IDs for relationships
cursor.execute("SELECT UserID FROM User")
user_ids = [row[0] for row in cursor.fetchall()]

# Company table
companies = []
for i in range(5):
    name = random_string(8).capitalize()
    location = random_string(10).capitalize()
    created_by = random.choice(user_ids)
    companies.append((name, created_by, location))

cursor.executemany(
    """
    INSERT INTO Company (Name, CreatedBy, Location)
    VALUES (%s, %s, %s)
    """,
    companies
)
connection.commit()

# Company IDs for relationships
cursor.execute("SELECT CompanyID FROM Company")
company_ids = [row[0] for row in cursor.fetchall()]

# Location table
locations = []
for company_id in company_ids:
    for _ in range(2):
        location_id = random.randint(1000, 9999)
        street = random_string(10).capitalize()
        city = random_string(7).capitalize()
        number = random.randint(1, 100)
        locations.append((location_id, company_id, number, street, city))

cursor.executemany(
    """
    INSERT INTO Location (LocationID, Company, Number, Street, City)
    VALUES (%s, %s, %s, %s, %s)
    """,
    locations
)
connection.commit()

# Location IDs for relationships
cursor.execute("SELECT LocationID FROM Location")
location_ids = [row[0] for row in cursor.fetchall()]

# JobOffer table
job_offers = []
for company_id in company_ids:
    for _ in range(3):
        location_id = random.choice(location_ids)
        created_by = random.choice(user_ids)
        status = random.choice(['open', 'closed'])
        date = random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        start_time = random.randint(8, 10)  # Start time (hours)
        end_time = start_time + random.randint(4, 8)  # End time (hours)
        max_wage = random.randint(500, 2000)
        working_days = random.randint(5, 7)
        hours = random.randint(20, 40)
        job_offers.append((location_id, created_by, status, date, start_time, end_time, max_wage, working_days, hours))

cursor.executemany(
    """
    INSERT INTO JobOffer (Location, CreatedBy, Status, Date, StartTime, EndTime, MaxWage, WorkingDays, Hours)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
    job_offers
)
connection.commit()

# JobOffer IDs for relationships
cursor.execute("SELECT JobOfferID FROM JobOffer")
job_offer_ids = [row[0] for row in cursor.fetchall()]

# Worker table
workers = []
for user_id in user_ids:
    experiences = random_string(50)
    description = random_string(30)
    workers.append((user_id, experiences, description))

cursor.executemany(
    """
    INSERT INTO Worker (UserID, Experiences, Description)
    VALUES (%s, %s, %s)
    """,
    workers
)
connection.commit()

# Worker IDs for relationships
cursor.execute("SELECT UserID FROM Worker")
worker_ids = [row[0] for row in cursor.fetchall()]

# Application table
applications = []
for job_offer_id in job_offer_ids:
    worker_id = random.choice(worker_ids)
    date = random_date(datetime(2024, 1, 1), datetime(2024, 12, 31))
    wage_offer = random.randint(500, 1500)
    applications.append((worker_id, job_offer_id, date, wage_offer))

cursor.executemany(
    """
    INSERT INTO Application (WorkerID, JobOfferID, Date, WageOffer)
    VALUES (%s, %s, %s, %s)
    """,
    applications
)
connection.commit()

# close
cursor.close()
connection.close()

print("Tables populated successfully!")