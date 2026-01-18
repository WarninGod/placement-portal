"""
Database Models for Placement Portal Application
Defines all tables and relationships using SQLAlchemy ORM
"""
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


from flask_login import UserMixin
class User(db.Model, UserMixin):
    """
    Central authentication table for all system users
    Supports three roles: admin, company, student
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'company', 'student'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return str(self.id)
    def is_authenticated(self):
        return True
    def is_active_user(self):
        return self.is_active and not self.is_blacklisted
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class CompanyProfile(db.Model):
    """
    Extended profile information for company users
    One-to-one relationship with User (role='company')
    """
    __tablename__ = 'company_profiles'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to users table (one-to-one)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Company details
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(200))
    website = db.Column(db.String(200))
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    description = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships (one-to-many with placement_drives)
    placement_drives = db.relationship('PlacementDrive', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CompanyProfile {self.company_name}>'


class StudentProfile(db.Model):
    """
    Extended profile information for student users
    One-to-one relationship with User (role='student')
    """
    __tablename__ = 'student_profiles'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to users table (one-to-one)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Student details
    full_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    department = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer)  # Current year of study (1, 2, 3, 4)
    cgpa = db.Column(db.Float)
    tenth_marks = db.Column(db.Float)  # 10th percentage
    twelfth_marks = db.Column(db.Float)  # 12th percentage
    dob = db.Column(db.Date)  # Date of birth
    resume_filename = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    skills = db.Column(db.Text)  # Comma-separated skills
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships (one-to-many with applications)
    applications = db.relationship('Application', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<StudentProfile {self.full_name} ({self.roll_number})>'


class PlacementDrive(db.Model):
    """
    Job/internship opportunities posted by companies
    Requires admin approval before visible to students
    """
    __tablename__ = 'placement_drives'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to company_profiles table (many-to-one)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    
    # Drive details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.String(50))  # 'Full-time', 'Internship', 'Part-time'
    location = db.Column(db.String(200))
    package = db.Column(db.String(100))  # Salary/stipend information
    eligibility_criteria = db.Column(db.Text)
    required_skills = db.Column(db.Text)
    application_deadline = db.Column(db.Date, nullable=False)
    
    # Approval and status flags
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships (one-to-many with applications)
    applications = db.relationship('Application', backref='drive', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PlacementDrive {self.title}>'


class Application(db.Model):
    """
    Records student applications to placement drives
    Resolves many-to-many relationship between students and drives
    Includes application status tracking
    """
    __tablename__ = 'applications'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys (creates many-to-many relationship)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    
    # Application status tracking
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'shortlisted', 'rejected', 'selected'
    remarks = db.Column(db.Text)  # Company's comments on the application
    
    # Timestamps
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Unique constraint to prevent duplicate applications
    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive_application'),
    )
    
    def __repr__(self):
        return f'<Application Student:{self.student_id} Drive:{self.drive_id} Status:{self.status}>'


class AdminAction(db.Model):
    """
    OPTIONAL: Audit trail for all admin actions
    Tracks who did what and when for accountability
    """
    __tablename__ = 'admin_actions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to users table (admin who performed action)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Action details
    action_type = db.Column(db.String(50), nullable=False)  # 'approve_company', 'approve_drive', 'blacklist_user', etc.
    target_id = db.Column(db.Integer)  # ID of affected entity
    target_type = db.Column(db.String(50))  # 'company', 'drive', 'student'
    remarks = db.Column(db.Text)
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to admin user
    admin = db.relationship('User', backref='actions')
    
    def __repr__(self):
        return f'<AdminAction {self.action_type} by Admin:{self.admin_id}>'
