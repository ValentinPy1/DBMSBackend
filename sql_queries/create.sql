
CREATE DATABASE IF NOT EXISTS Job2main
    DEFAULT CHARACTER SET = 'utf8mb4';

USE Job2main;

-- Table: User
CREATE TABLE IF NOT EXISTS User (
    UserID INT PRIMARY KEY,
    FirstName VARCHAR(255),
    Surname VARCHAR(255),
    Name VARCHAR(255),
    Email VARCHAR(255),
    PhoneNumber VARCHAR(255)
);
-- Table: Company
CREATE TABLE IF NOT EXISTS Company (
    CompanyID INT PRIMARY KEY,
    CreatedBy INT,
    Name VARCHAR(255),
    Location VARCHAR(255)
);

-- Table: Employer
CREATE TABLE IF NOT EXISTS Employer (
    Company INT,
    UserID INT,
    FOREIGN KEY (Company) REFERENCES Company(CompanyID),
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);

-- Alter Table: Company to add foreign key constraint
ALTER TABLE Company
ADD CONSTRAINT fk_createdby FOREIGN KEY (CreatedBy) REFERENCES Employer(UserID);

-- Table: Worker
CREATE TABLE IF NOT EXISTS Worker (
    UserID INT,
    Experiences TEXT,
    Description TEXT,
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);

-- Table: Location
CREATE TABLE IF NOT EXISTS Location (
    LocationID INT PRIMARY KEY,
    Company INT,
    Number VARCHAR(255),
    Street VARCHAR(255),
    City VARCHAR(255),
    FOREIGN KEY (Company) REFERENCES Company(CompanyID)
);

-- Table: JobOffer
CREATE TABLE IF NOT EXISTS JobOffer (
    JobOfferID INT PRIMARY KEY,
    Location INT,
    CreatedBy INT,
    Status ENUM('Open', 'Confirmed', 'Running', 'Completed') NOT NULL,
    Date DATE,
    StartTime TIME,
    EndTime TIME,
    MaxWage DECIMAL(10, 2),
    WorkingDays INT,
    Hours INT,
    FOREIGN KEY (Location) REFERENCES Location(LocationID),
    FOREIGN KEY (CreatedBy) REFERENCES Employer(UserID)
);
-- Table: Application
CREATE Table IF NOT EXISTS Application (
    WorkerID INT,
    JobOfferID INT,
    Status ENUM('Pending', 'Refused', 'Accepted') NOT NULL,
    Date DATE,
    WageOffer DECIMAL(10, 2),
    FOREIGN KEY (WorkerID) REFERENCES Worker(UserID),
    FOREIGN KEY (JobOfferID) REFERENCES JobOffer(JobOfferID)
);
