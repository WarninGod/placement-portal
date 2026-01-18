# PLACEMENT PORTAL APPLICATION

## Project Overview
A Flask-based web application for managing campus placement activities with three user roles: Admin, Company, and Student.

## Current Status: BASE PROJECT CREATED ✓

### What Has Been Completed:

1. **Planning Documents**
   - `PLANNING_DOCUMENT.txt` - Comprehensive architecture and design plan
   - `VIVA_QUESTIONS.txt` - 43 viva questions with detailed answers

2. **Project Structure**
   ```
   Placement drive/
   ├── app/
   │   ├── __init__.py          # Flask app factory
   │   ├── models.py            # Database models (5 tables)
   │   └── utils.py             # Helper functions & decorators
   ├── instance/                # SQLite database location
   ├── config.py                # Configuration settings
   ├── run.py                   # Application entry point
   └── requirements.txt         # Python dependencies
   ```

3. **Database Models Created**
   - **User** - Central authentication (admin/company/student)
   - **CompanyProfile** - Company-specific information
   - **StudentProfile** - Student-specific information
   - **PlacementDrive** - Job postings by companies
   - **Application** - Student applications to drives
   - **AdminAction** - Audit trail (optional)

4. **Key Features Implemented**
   - SQLite database programmatically created
   - Password hashing (secure storage)
   - Role-based access control decorators
   - Default admin user auto-creation
   - One-to-one and one-to-many relationships
   - Unique constraints to prevent duplicate applications

## Installation & Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python run.py
```

### Step 3: Access the Application
Open browser and navigate to: `http://127.0.0.1:5000`

### Default Admin Credentials
- **Email:** admin@placement.com
- **Password:** admin123
- ⚠️ Change password after first login!

## Database Schema

### users table
- id, email, password_hash, role, is_active, is_approved, is_blacklisted
- Roles: 'admin', 'company', 'student'

### company_profiles table
- id, user_id (FK), company_name, industry, location, website, contact info

### student_profiles table
- id, user_id (FK), full_name, roll_number, department, graduation_year, cgpa, resume

### placement_drives table
- id, company_id (FK), title, description, job_type, package, deadline, is_approved

### applications table
- id, student_id (FK), drive_id (FK), status, applied_at
- UNIQUE(student_id, drive_id) - prevents duplicate applications

## Key Design Decisions

1. **SQLite Database** - Lightweight, portable, no server required
2. **Approval Workflows** - Companies and drives require admin approval
3. **Password Security** - Werkzeug password hashing (pbkdf2:sha256)
4. **Role-Based Access** - Decorators enforce permissions
5. **Soft Deletion** - Flags instead of DELETE for audit trail
6. **Unique Constraints** - Database-level duplicate prevention

## What's Next?

Templates and routes will be created in the next phase:
- Authentication routes (login, register, logout)
- Admin dashboard and management routes
- Company dashboard and drive creation
- Student dashboard and application system
- Jinja2 templates with Bootstrap styling

## Project Files Explained

### config.py
Configuration settings for database, uploads, and security

### app/__init__.py
Flask application factory that creates and configures the app

### app/models.py
SQLAlchemy models defining all database tables with relationships

### app/utils.py
Helper functions including decorators and admin user creation

### run.py
Entry point to start the Flask development server

## Testing Database Creation

After running `python run.py`, check:
1. `instance/placement.db` file is created
2. Console shows "✓ Default admin user created successfully"
3. No error messages in terminal

## Technology Stack

- **Backend:** Flask 3.0.0
- **Database:** SQLite (programmatically created)
- **ORM:** Flask-SQLAlchemy 3.1.1
- **Security:** Werkzeug password hashing
- **Frontend:** (To be added) Jinja2 + Bootstrap

## Notes for Viva

- All passwords are hashed (never stored as plain text)
- Foreign keys enforce referential integrity
- Unique constraints prevent duplicate applications
- Role-based decorators provide access control
- Admin is pre-existing (no registration route)
- Companies require approval; students are auto-approved
- Audit trail table tracks all admin actions

## Troubleshooting

**Database not created?**
- Check if `instance/` folder exists
- Verify file permissions

**Import errors?**
- Run: `pip install -r requirements.txt`
- Ensure virtual environment is activated

**Port 5000 already in use?**
- Change port in run.py: `app.run(port=5001)`

---

Created for college placement management system project.
Academic evaluation and viva ready! 🎓
