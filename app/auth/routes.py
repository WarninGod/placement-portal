"""
Authentication routes for Placement Portal
Handles login, logout, registration (company, student)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, CompanyProfile, StudentProfile
from werkzeug.security import generate_password_hash, check_password_hash

# Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# Landing page
@auth_bp.route('/')
def index():
    return render_template('index.html')

# Login route (all roles)
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            # Block blacklisted or inactive users
            if user.is_blacklisted or not user.is_active:
                flash('Account is deactivated or blacklisted.', 'danger')
                return redirect(url_for('auth.login'))
            # Block unapproved companies
            if user.role == 'company' and not user.is_approved:
                flash('Company account pending admin approval.', 'warning')
                return redirect(url_for('auth.login'))
            login_user(user)
            session['role'] = user.role
            session['is_approved'] = user.is_approved
            return redirect(url_for(f'{user.role}.dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

# Logout route
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))

# Student registration
@auth_bp.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        roll_number = request.form['roll_number']
        department = request.form['department']
        graduation_year = int(request.form['graduation_year'])
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.student_register'))
        if StudentProfile.query.filter_by(roll_number=roll_number).first():
            flash('Roll number already exists.', 'danger')
            return redirect(url_for('auth.student_register'))
        user = User(email=email, role='student', is_active=True, is_approved=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # Calculate year of study based on graduation year
        # Assuming 4-year program: if graduation is 2026 and current year is 2026, they're in 4th year
        from datetime import date
        current_year = date.today().year
        year_of_study = 4 - (graduation_year - current_year)
        # Clamp between 1 and 4
        year_of_study = max(1, min(4, year_of_study))
        profile = StudentProfile(user_id=user.id, full_name=full_name, roll_number=roll_number, department=department, graduation_year=graduation_year, year=year_of_study)
        db.session.add(profile)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('student_register.html')

# Company registration
@auth_bp.route('/company/register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        company_name = request.form['company_name']
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.company_register'))
        user = User(email=email, role='company', is_active=True, is_approved=False)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        profile = CompanyProfile(user_id=user.id, company_name=company_name)
        db.session.add(profile)
        db.session.commit()
        flash('Registration successful. Await admin approval.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('company_register.html')
