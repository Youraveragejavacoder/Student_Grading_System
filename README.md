# Grading System

## Project Description

The Grading System is a desktop application for managing student records and academic grades. It provides a graphical interface for authorized users to create accounts, sign in, manage students, record grades, and view dashboard statistics.

The system addresses the need for a simple and organized alternative to manually tracking student information and grades. It keeps related records in one SQLite database, validates user input, prevents duplicate records, and removes a student's related grades when the student is permanently deleted.

## Project Objectives

- Provide a clear graphical interface for managing academic records.
- Store student, grade, and user information in a structured SQLite database.
- Allow users to create, read, update, delete, and search records.
- Validate student IDs, names, subjects, scores, and account information.
- Keep student and grade records consistent through database relationships.
- Provide dashboard statistics for total students, grade records, and average score.
- Apply role-based permissions for administrators, teachers, and students.

## Features

### Authentication

- User registration with username and password validation.
- User login and logout.
- SHA-256 password hashing before passwords are stored.
- Role information for administrators, teachers, and students.

### Student Management

- Add a student using a five-digit number and four-digit year format, such as `12345-2026`.
- Require newly added student IDs to use the current calendar year.
- Display all students in a searchable table.
- Search for a student by Student ID.
- Update a student's name.
- Permanently delete a student and all related grade records.
- Clear form inputs without changing saved records.

### Grade Management

- Load a student's gradebook by Student ID.
- Add a subject and score from `0.00` to `100.00`.
- Prevent duplicate subjects for the same student.
- Update an existing score.
- Permanently delete a grade record.
- Refresh the visible grade table after changes.

### Dashboard

- Display the total number of students.
- Display the total number of grade records.
- Display the current average score.
- Refresh dashboard statistics.

### User Interface

- PyQt6 desktop interface with separate login, registration, dashboard, student, and grade views.
- Shared QSS styling for a consistent visual design.
- Side notifications for successful add, update, and delete operations.
- Form validation messages for invalid or missing input.

## Technologies Used

- **Programming language:** Python 3
- **GUI framework:** PyQt6
- **Database:** SQLite through Python's built-in `sqlite3` module
- **Data modeling:** Python `dataclasses`
- **Password hashing:** Python `hashlib`
- **Styling:** Qt Style Sheets (`.qss`)
- **Development tools:** Virtual environment and Git

## Project Structure

```text
Project in python/
├── main.py
├── README.md
├── .gitignore
├── style.qss
├── database/
│   └── database.py
└── features/
    ├── Auth/
    │   ├── model.py
    │   ├── repository.py
    │   ├── service.py
    │   ├── style.qss
    │   └── view.py
    ├── dashboard/
    │   ├── model.py
    │   ├── repository.py
    │   ├── service.py
    │   ├── style.qss
    │   ├── toast.py
    │   └── view.py
    ├── grades/
    │   ├── model.py
    │   ├── repository.py
    │   ├── service.py
    │   ├── style.qss
    │   └── view.py
    └── students/
        ├── model.py
        ├── repository.py
        ├── service.py
        ├── style.qss
        └── view.py
```

### Important Files and Folders

- `main.py` creates the application, database, repositories, services, and main window.
- `database/database.py` creates the SQLite database connection and validates the database schema.
- `features/Auth/` contains authentication models, database operations, business logic, and login or registration views.
- `features/students/` contains student validation, student database operations, student logic, and the student management view.
- `features/grades/` contains grade validation, grade database operations, grade logic, and the grade management view.
- `features/dashboard/` contains dashboard statistics, role permissions, the main application window, and side notifications.
- `style.qss` contains the main application theme.
- `.gitignore` prevents virtual environments, cache files, IDE settings, secrets, build files, and database files from being committed.

## Installation and Setup

### Requirements

- Python 3.10 or newer is recommended.
- PyQt6.

### Windows Setup

Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install PyQt6
```

If PowerShell blocks activation, the application can still be run using the virtual environment's Python executable:

```powershell
.venv\Scripts\python.exe main.py
```

### macOS or Linux Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install PyQt6
```

Run the application with:

```bash
python main.py
```

The application automatically creates `grading_system.db` in the project folder the first time it starts. Database files are ignored by Git through `.gitignore`.

## How to Use the System

1. Start the application with `python main.py`.
2. Create an account from the registration screen, or sign in with an existing account.
3. Use the sidebar to open the Dashboard, Students, or Grades section.
4. In **Students**, enter a Student ID such as `12345-2026` and a full name, then select **Add student**.
5. Select a student row to populate the form when updating or deleting a student.
6. In **Grades**, enter the student's ID and select **Load grades**.
7. Enter a subject and score, then select **Add grade**.
8. Select a grade row to populate the form when updating or deleting a grade.
9. Use **Clear** to empty form fields without changing database records.
10. Use **Refresh metrics** on the Dashboard to update the displayed statistics.

Deleting a student permanently removes the student and all grades associated with that Student ID. The Grades view also clears matching rows immediately when the deletion occurs.

## OOP Implementation

The project uses object-oriented programming to separate data, database access, business rules, and user interface responsibilities.

### Important Classes and Objects

- `Database` manages database initialization, table creation, schema checks, and SQLite connections.
- `Student` is a dataclass representing a student and validating Student ID and name values.
- `Grade` is a dataclass representing a grade and validating Student ID, subject, and score values.
- `User` is a dataclass representing a user account.
- `StudentRepository` performs database operations for students.
- `GradeRepository` performs database operations for grades.
- `AuthenticationRepository` performs database operations for users.
- `StudentService` applies student-related business rules before using the repository.
- `GradeService` applies grade-related business rules before using the repository.
- `AuthenticationService` handles registration, password hashing, login, and logout.
- `DashboardRepository` calculates dashboard statistics.
- `UIService` provides dashboard statistics and role permissions.
- `StudentsView` provides the student management interface.
- `GradesView` provides the grade management interface.
- `DashboardWidget` displays dashboard statistics and actions.
- `GradingSystemUI` is the main application window and connects the different views.

### Encapsulation

Encapsulation is applied by keeping responsibilities inside focused classes. For example, database queries are kept in repository classes, validation is kept in model classes, and application rules are kept in service classes. Internal helper methods such as `_load_students`, `_populate_grades`, and `_update_empty_state` are kept within their views.

### Inheritance

The interface classes inherit from PyQt6 widget classes:

- `StudentsView` inherits from `QWidget`.
- `GradesView` inherits from `QWidget`.
- `DashboardWidget` inherits from `QWidget`.
- `GradingSystemUI` inherits from `QMainWindow`.
- `AuthView` inherits from `QStackedWidget`.

This allows the project to extend PyQt6 components with application-specific layouts, controls, and behavior.

### Polymorphism

Polymorphism is primarily provided through PyQt6's widget and signal system. Application-specific views can be used as standard Qt widgets, while their connected methods provide different behavior for actions such as button clicks and table selections. The repository and service classes also expose consistent operation patterns for different data types, such as adding, reading, updating, and removing records.

## Database

The system uses one SQLite database named `grading_system.db`. The database path is defined in `database/database.py`, and foreign-key enforcement is enabled for every connection.

### Tables

#### `users`

| Column | Description |
| --- | --- |
| `id` | Auto-incrementing primary key |
| `username` | Unique username |
| `password` | Hashed password |
| `role` | User role, such as `admin`, `teacher`, or `student` |

#### `students`

| Column | Description |
| --- | --- |
| `student_id` | Primary key using the `00000-YYYY` format |
| `name` | Student's full name |

#### `grades`

| Column | Description |
| --- | --- |
| `student_id` | Foreign key referencing `students.student_id` |
| `subject` | Subject name |
| `score` | Numeric score from `0` to `100` |

The `grades` table uses a composite primary key made from `student_id` and `subject`, so a student cannot have two grade records for the same subject. The foreign key uses `ON DELETE CASCADE`, so grades are removed when their student is deleted.

### Database Operations

- **Create:** Creates users, students, and grades tables when the application starts. Repositories insert new users, students, and grades.
- **Read:** Retrieves one user, student, or grade; lists all students; loads all grades for a student; and calculates dashboard statistics.
- **Update:** Changes a student's name or updates a grade score.
- **Delete:** Removes a grade or permanently removes a student and all related grades.
- **Search:** Finds a student by Student ID and loads grade records by Student ID.

## Data Validation

- Student IDs must match `00000-YYYY`.
- Newly added student IDs must use the current calendar year.
- Student names and subjects cannot be empty.
- Scores must be numeric values between `0.0` and `100.0`.
- Duplicate Student IDs are rejected.
- Duplicate subjects for the same student are rejected.
- Usernames must be between 3 and 30 characters.
- Passwords must contain at least 6 characters.

## Screenshots
<img width="1920" height="1080" alt="Screenshot (538)" src="https://github.com/user-attachments/assets/f3dc1de7-ee2f-4cc7-a4b2-308945641b14" />
User Authentication, Registration and Validation
<br>
<img width="1920" height="1080" alt="Screenshot (539)" src="https://github.com/user-attachments/assets/35411ea2-7bf0-4c02-8d8c-4d1ccc879b90" />
Dashboard Overview
<br>
<img width="1920" height="1080" alt="Screenshot (540)" src="https://github.com/user-attachments/assets/2ca4821c-7369-426b-958e-1fd11b9c96f7" />
Input student Information
<br>
<img width="1920" height="1080" alt="Screenshot (541)" src="https://github.com/user-attachments/assets/3cae774f-fa05-491e-9d03-ed80175dab56" />
Student Id validation, Subjects and Grades Information
<br>

## Testing

The system was tested through various error-testing scenarios, including user authentication and user validation. We also tested student input validation by entering different ID patterns that did not follow the required `00000-2026` format or valid calendar values. These inputs resulted in errors, confirming that the system’s error handling was effective. Grade validation was also tested by entering values below 0 and above 100, which correctly resulted in errors and confirmed that the value validation was working properly.

We expected the system to prevent errors during user authentication, avoid SQL injection, and provide consistent results when testing the student and grade features. The actual results matched our expectations, showing that the system’s validation and error-handling features worked as intended.


