#### Setup env :
##### On linux :
`source venv/bin/activate`

##### On windows :
`venv\Scripts\activate`

#### Then Run :
`python app.py`	



## Requirements

### Employers :

#### Company lifecycle :

- POST create a company
- UPDATE join a company with company ID
- UPDATE Quit a company
- POST create a new location for the company
- DELETE a location for the company

#### Job Lifecycle :

- POST create a new joboffer with default status
- GET My Job offers with a status filter optional argument

#### Workers management :

- UPDATE the status of an application from pending to refused or accepted
- GET all workers

### Workers :

- GET all available jobs
- POST application to a specific job with a wage request
- GET all my application with optional filter on status (joined with the realted joboffer)
- GET employer and company from a job offer id