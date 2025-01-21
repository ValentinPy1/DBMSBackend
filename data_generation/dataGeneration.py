import random
from datetime import datetime, timedelta
import csv

def write_csv(filename, headers, data):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

class DataGenerator:
    def __init__(self, num_users, num_employers, num_companies, num_job_offers, num_applications):
        self.num_users = num_users
        self.num_employers = num_employers  # New parameter
        self.num_companies = num_companies
        self.num_job_offers = num_job_offers
        self.num_applications = num_applications
        
        # Store IDs for reference
        self.employer_ids = []
        self.worker_ids = []

    def generate_users_and_split(self):
        users = []
        # Generate all users first
        for i in range(1, self.num_users + 1):
            users.append({
                "UserID": i,
                "FirstName": f"First{i}",
                "Surname": f"Last{i}",
                "Name": f"First{i} Last{i}",
                "Email": f"user{i}@example.com",
                "PhoneNumber": f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}"
            })
        
        # Randomly select employer IDs
        self.employer_ids = random.sample(range(1, self.num_users + 1), self.num_employers)
        # Remaining IDs are workers
        self.worker_ids = [i for i in range(1, self.num_users + 1) if i not in self.employer_ids]
        
        return users

    def generate_employers(self):
        employers = []
        for user_id in self.employer_ids:
            employers.append({
                "CompanyID": None,  # Will be updated after company creation
                "UserID": user_id
            })
        return employers

    def generate_companies(self):
        companies = []
        # First create companies without CreatedBy
        for i in range(1, self.num_companies + 1):
            companies.append({
                "CompanyID": i,
                "CreatedBy": random.choice(self.employer_ids),  # Randomly assign an employer
                "Name": f"Company{i}",
                "Location": f"City{i}"
            })
        return companies

    def update_employers_with_companies(self, employers, companies):
        # Make sure each company gets exactly one employer
        company_employer_pairs = []
        available_employers = self.employer_ids.copy()
        
        # First, assign one unique employer to each company
        for company in companies:
            if not available_employers:  # If we run out of employers
                raise ValueError("Not enough employers for companies. Each company needs a unique employer.")
            
            # Pick a random employer from available ones
            employer_id = random.choice(available_employers)
            available_employers.remove(employer_id)  # Remove this employer from available pool
            
            # Update company's CreatedBy
            company["CreatedBy"] = employer_id
            company_employer_pairs.append((company["CompanyID"], employer_id))
        
        # Now update employers list with company assignments
        updated_employers = []
        for employer in employers:
            # Find if this employer was assigned a company
            assigned_company = next(
                (pair[0] for pair in company_employer_pairs if pair[1] == employer["UserID"]), 
                None
            )
            updated_employers.append({
                "CompanyID": assigned_company,  # Will be None if employer wasn't assigned a company
                "UserID": employer["UserID"]
            })
        
        return updated_employers

    def generate_workers(self):
        workers = []
        for user_id in self.worker_ids:  # Only use non-employer user IDs
            workers.append({
                "UserID": user_id,
                "Experiences": f"Experience for User{user_id}",
                "Description": f"Worker{user_id} description"
            })
        return workers

    def generate_locations(self, companies):
        locations = []
        # Generate exactly one location for each company
        for company in companies:
            locations.append({
                "LocationID": company["CompanyID"],  # Match LocationID with CompanyID for simplicity
                "CompanyID": company["CompanyID"],
                "Number": str(random.randint(1, 999)),  # Building number
                "Street": f"Street{random.randint(1, 50)}",  # More variety in street names
                "City": random.choice([  # List of actual cities for more realism
                    "Istanbul", "Ankara", "Izmir", "Antalya", "Bursa",
                    "Eskisehir", "Konya", "Trabzon", "Gaziantep", "Adana"
                ])
            })
        return locations
    
    def generate_job_offers(self, locations):
        job_offers = []
        for i in range(1, self.num_job_offers + 1):
            location = random.choice(locations)
            created_by = random.choice(self.employer_ids)  # Only employers can create job offers
            job_offers.append({
                "JobOfferID": i,
                "LocationID": location["LocationID"],
                "CreatedBy": created_by,
                "Status": random.choice(["Open", "Confirmed", "Running", "Completed"]),
                "Date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
                "StartTime": "09:00:00",
                "EndTime": "17:00:00",
                "MaxWage": round(random.uniform(20.0, 50.0), 2),
                "WorkingDays": random.randint(1, 5),
                "Hours": random.randint(4, 8)
            })
        return job_offers

    def generate_applications(self, job_offers):
        applications = []
        for i in range(1, self.num_applications + 1):
            worker_id = random.choice(self.worker_ids)  # Only workers can apply
            job_offer_id = random.choice(job_offers)["JobOfferID"]
            applications.append({
                "WorkerID": worker_id,
                "JobOfferID": job_offer_id,
                "Status": random.choice(["Pending", "Accepted", "Refused"]),
                "Date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "WageOffer": round(random.uniform(15.0, 45.0), 2)
            })
        return applications

# Main execution
num_users = 100  # Total users
num_employers = 20  # Subset of users who are employers
num_companies = 20 # This will also be the number of locations
num_job_offers = 30
num_applications = 40

data_gen = DataGenerator(num_users, num_employers, num_companies, num_job_offers, num_applications)

# Generate data in correct order
users = data_gen.generate_users_and_split()
employers = data_gen.generate_employers()
companies = data_gen.generate_companies()
employers = data_gen.update_employers_with_companies(employers, companies)
locations = data_gen.generate_locations(companies)
workers = data_gen.generate_workers()
job_offers = data_gen.generate_job_offers(locations)
applications = data_gen.generate_applications(job_offers)

# Write CSV files
write_csv("User.csv", ["UserID", "FirstName", "Surname", "Name", "Email", "PhoneNumber"], users)
write_csv("Employer.csv", ["CompanyID", "UserID"], employers)
write_csv("Company.csv", ["CompanyID", "CreatedBy", "Name", "Location"], companies)
write_csv("Location.csv", ["LocationID", "CompanyID", "Number", "Street", "City"], locations)
write_csv("Worker.csv", ["UserID", "Experiences", "Description"], workers)
write_csv("JobOffer.csv", ["JobOfferID", "LocationID", "CreatedBy", "Status", "Date", "StartTime", "EndTime", "MaxWage", "WorkingDays", "Hours"], job_offers)
write_csv("Application.csv", ["WorkerID", "JobOfferID", "Status", "Date", "WageOffer"], applications)