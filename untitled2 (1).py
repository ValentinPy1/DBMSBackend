# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1cIoLzixD4phaNrP4cp7zgzNCHoPlr8l_
"""

import csv

users = [
    {"UserID": 1, "FirstName": "John", "Surname": "Smith", "Name": "John Smith", "Email": "john.smith@example.com", "PhoneNumber": "+1-555-123-4567"},
    {"UserID": 2, "FirstName": "Emily", "Surname": "Johnson", "Name": "Emily Johnson", "Email": "emily.johnson@example.com", "PhoneNumber": "+1-555-234-5678"},
    {"UserID": 3, "FirstName": "Michael", "Surname": "Williams", "Name": "Michael Williams", "Email": "michael.williams@example.com", "PhoneNumber": "+1-555-345-6789"},
    {"UserID": 4, "FirstName": "Sarah", "Surname": "Brown", "Name": "Sarah Brown", "Email": "sarah.brown@example.com", "PhoneNumber": "+1-555-456-7890"},
    {"UserID": 5, "FirstName": "David", "Surname": "Jones", "Name": "David Jones", "Email": "david.jones@example.com", "PhoneNumber": "+1-555-567-8901"}
]

companies = [
    {"CompanyID": 1, "Name": "Tech Innovators LLC", "Location": "San Francisco, CA"},
    {"CompanyID": 2, "Name": "Global Solutions Inc.", "Location": "New York, NY"},
    {"CompanyID": 3, "Name": "Green Energy Systems", "Location": "Austin, TX"},
    {"CompanyID": 4, "Name": "Creative Design Co.", "Location": "Los Angeles, CA"},
    {"CompanyID": 5, "Name": "Sarajevo Tech Hub", "Location": "Sarajevo, Bosnia"}
]

employers = [
    {"Company": 1, "UserID": 1},
    {"Company": 2, "UserID": 3},
    {"Company": 3, "UserID": 4},
    {"Company": 4, "UserID": 2},
    {"Company": 5, "UserID": 5}
]

workers = [
    {"UserID": 2, "Experiences": "5 years as a software engineer", "Description": "Expert in backend development and databases."},
    {"UserID": 3, "Experiences": "3 years as a project manager", "Description": "Skilled in leading IT teams and project organization."},
    {"UserID": 4, "Experiences": "2 years as a graphic designer", "Description": "Creative designer specializing in branding and visuals."},
    {"UserID": 5, "Experiences": "4 years as a civil engineer", "Description": "Experienced in construction project management."}
]

locations = [
    {"LocationID": 1, "Company": 1, "Number": "123", "Street": "Main St.", "City": "San Francisco"},
    {"LocationID": 2, "Company": 2, "Number": "456", "Street": "Broadway", "City": "New York"},
    {"LocationID": 3, "Company": 3, "Number": "789", "Street": "Market St.", "City": "Austin"},
    {"LocationID": 4, "Company": 4, "Number": "101", "Street": "Sunset Blvd.", "City": "Los Angeles"},
    {"LocationID": 5, "Company": 5, "Number": "202", "Street": "Titova St.", "City": "Sarajevo"}
]

job_offers = [
    {"JobOfferID": 1, "Location": 1, "CreatedBy": 1, "Status": "Open", "Date": "2023-12-01", "StartTime": "09:00:00", "EndTime": "17:00:00", "MaxWage": 45.00, "WorkingDays": 5, "Hours": 8},
    {"JobOfferID": 2, "Location": 2, "CreatedBy": 3, "Status": "Closed", "Date": "2023-11-15", "StartTime": "08:00:00", "EndTime": "16:00:00", "MaxWage": 50.00, "WorkingDays": 5, "Hours": 8},
    {"JobOfferID": 3, "Location": 3, "CreatedBy": 4, "Status": "Open", "Date": "2023-12-10", "StartTime": "10:00:00", "EndTime": "18:00:00", "MaxWage": 40.00, "WorkingDays": 4, "Hours": 8}
]

applications = [
    {"WorkerID": 2, "JobOfferID": 1, "Date": "2023-12-02", "WageOffer": 42.00},
    {"WorkerID": 3, "JobOfferID": 2, "Date": "2023-11-16", "WageOffer": 48.00},
    {"WorkerID": 4, "JobOfferID": 3, "Date": "2023-12-11", "WageOffer": 38.00}
]


def write_csv(filename, fieldnames, rows):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

write_csv("User.csv", ["UserID", "FirstName", "Surname", "Name", "Email", "PhoneNumber"], users)
write_csv("Company.csv", ["CompanyID", "Name", "Location"], companies)
write_csv("Employer.csv", ["Company", "UserID"], employers)
write_csv("Worker.csv", ["UserID", "Experiences", "Description"], workers)
write_csv("Location.csv", ["LocationID", "Company", "Number", "Street", "City"], locations)
write_csv("JobOffer.csv", ["JobOfferID", "Location", "CreatedBy", "Status", "Date", "StartTime", "EndTime", "MaxWage", "WorkingDays", "Hours"], job_offers)
write_csv("Application.csv", ["WorkerID", "JobOfferID", "Date", "WageOffer"], applications)

print("Generated CSV files:")
for file_name in ["User.csv", "Company.csv", "Employer.csv", "Worker.csv", "Location.csv", "JobOffer.csv", "Application.csv"]:
    print(f"- {file_name}")
    from google.colab import files

files.download("User.csv")
files.download("Company.csv")
files.download("Employer.csv")
files.download("Worker.csv")
files.download("Location.csv")
files.download("JobOffer.csv")
files.download("Application.csv")