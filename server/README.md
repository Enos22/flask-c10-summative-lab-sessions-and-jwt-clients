1. Team task allocation
Enos arenga  Authentication & Users
Member 1
Files:
* routes/auth.py
* models/user.py
* schemas/user_schema.py
Responsibilities:
* User registration.
* Login and logout.
* Password hashing.
* Authentication and user access protection.



Benson maina Medication Management
Member 2
Files:
* routes/medications.py
* models/medication.py
* schemas/medication_schema.py
Responsibilities:
* Add medications.
* View medications.
* Update medication details.
* Delete medications.



Samadi  Medication Scheduling
Member 3
Files:
* routes/schedules.py
* models/medication_schedule.py
* schemas/schedule_schema.py
Responsibilities:
* Create medication schedules.
* Set reminder times.
* Manage days of the week.
* Update and delete schedules.

Waynemarkouma  Dose Tracking
Member 4
Files:
* routes/doses.py
* models/dose.py
* schemas/dose_schema.py
Responsibilities:
* Display scheduled doses.
* Mark doses as taken.
* Mark doses as missed.
* Record when medication was taken.
Faith  Reminders & Reports
Member 5
Files:
* routes/reports.py
* services/reminder_service.py
* services/adherence_service.py
Responsibilities:
* Identify upcoming medication reminders.
* Calculate medication adherence.
* Generate daily reports.
* Display missed and completed doses.


2. Shared backend structure
Everyone should follow the same folder structure.
backend/
?
??? app/
?   ??? __init__.py
?   ??? config.py
?   ?
?   ??? models/
?   ?   ??? user.py
?   ?   ??? medication.py
?   ?   ??? medication_schedule.py
?   ?   ??? dose.py
?   ?
?   ??? routes/
?   ?   ??? auth.py
?   ?   ??? medications.py
?   ?   ??? schedules.py
?   ?   ??? doses.py
?   ?   ??? reports.py
?   ?
?   ??? schemas/
?   ??? services/
?   ??? extensions.py
?
??? migrations/
??? tests/
??? requirements.txt
??? run.py
3. How the five collaborators will work together
Stage
Responsibility
1
Agree on database models and relationships.
2
Each member develops their assigned module.
3
Each member tests their API endpoints.
4
Merge the five modules into the main branch.
5
Test the complete backend together.
6
Connect the backend to React.
4. Important team rules
To avoid Git conflicts:
* Each collaborator should work on a separate feature branch.
* Do not let everyone edit app/__init__.py, extensions.py, or requirements.txt independently.
* Agree on database relationships and API response formats before development.
* One person should coordinate migrations to prevent conflicting database changes.
* Merge completed work through pull requests.
5. Recommended responsibility for the team lead
The team lead should coordinate the shared application setup, database configuration, migrations, code reviews, and final integration.


# MORE on individual tasks

MediReminder  Backend Structure
For MediReminder, we will use Python, Flask, SQLAlchemy, SQLite, Flask-Migrate, and Marshmallow.
The backend is responsible for storing medication information, managing schedules, tracking doses, and providing data to the React frontend through REST APIs.
1. Project folder structure
medireminder/
?
??? backend/
?   ?
?   ??? app/
?   ?   ??? __init__.py
?   ?   ??? config.py
?   ?   ?
?   ?   ??? models/
?   ?   ?   ??? __init__.py
?   ?   ?   ??? user.py
?   ?   ?   ??? medication.py
?   ?   ?   ??? medication_schedule.py
?   ?   ?   ??? dose.py
?   ?   ?
?   ?   ??? routes/
?   ?   ?   ??? __init__.py
?   ?   ?   ??? auth.py
?   ?   ?   ??? medications.py
?   ?   ?   ??? schedules.py
?   ?   ?   ??? doses.py
?   ?   ?   ??? reports.py
?   ?   ?
?   ?   ??? schemas/
?   ?   ?   ??? user_schema.py
?   ?   ?   ??? medication_schema.py
?   ?   ?   ??? schedule_schema.py
?   ?   ?   ??? dose_schema.py
?   ?   ?
?   ?   ??? services/
?   ?       ??? reminder_service.py
?   ?       ??? adherence_service.py
?   ?
?   ??? migrations/
?   ??? instance/
?   ?   ??? medireminder.db
?   ?
?   ??? tests/
?   ??? requirements.txt
?   ??? run.py
?
??? frontend/
2. Explanation of each folder
A. Models  Database structure
The models define how information is stored in the database.
Model
Responsibility
User
Stores user account information.
Medication
Stores medication names, dosage, and instructions.
MedicationSchedule
Stores medication times and selected days.
Dose
Tracks whether a scheduled dose is taken, missed, or pending.
B. Routes  API endpoints
Routes receive requests from the React frontend and return responses.
Route
Responsibility
Auth
Registration, login, and logout.
Medications
Add, view, update, and delete medications.
Schedules
Create and manage medication schedules.
Doses
Mark doses as taken or missed.
Reports
Display daily and historical adherence reports.
C. Schemas  Data validation
Schemas ensure that information received from the frontend is valid.
For example:
* Medication name should not be empty.
* Dosage should be provided.
* Scheduled time should be valid.
* Dose status should be an accepted value.
D. Services  Business logic
This folder handles operations that are more complex than simply receiving API requests.
* Reminder Service: Determines which medication reminders are due.
* Adherence Service: Calculates how consistently users follow their medication schedules.
E. Migrations  Database changes
Flask-Migrate manages changes to the database structure.
For example, if we add a new column to the Medication table, migrations help update the database without manually rebuilding it.
F. Tests  Backend testing
Tests verify that the backend works correctly, including medication creation, schedule management, dose tracking, and authentication.
3. How the database tables relate
USER
One user can have many medications
One-to-Many
MEDICATION
Each medication belongs to one user
One-to-Many
SCHEDULE
When to take it
One-to-Many
DOSE
Taken, missed, pending
A dose record represents a particular scheduled occurrence of a medication.
4. How the backend communicates with React
The communication happens through REST APIs.
React Frontend
User adds a medication
Flask REST API
Receives and processes the request
SQLAlchemy
Communicates with the database
SQLite Database
Stores medication information
Example workflow:
1. A user adds a medication in React.
2. React sends a POST request to Flask.
3. Flask validates the information.
4. SQLAlchemy saves it in SQLite.
5. Flask returns a response.
6. React displays the saved medication.
5. Important backend concepts to understand
Technology
What it does
Flask
Builds the backend application.
SQLAlchemy
Connects Python models to database tables.
SQLite
Stores application data.
Flask-Migrate
Manages database structure changes.
Marshmallow
Validates and serializes data.
REST API
Connects the frontend and backend.
My recommendation: Build MediReminder in this order:
1. Database models and relationships.
2. Flask application setup.
3. Database migrations.
4. Medication CRUD APIs.
5. Medication schedule APIs.
6. Dose tracking APIs.
7. Authentication.
8. Reminder and adherence services.
9. Reports and testing.
