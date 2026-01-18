"""
Student routes for Placement Portal
Dashboard, drive browsing, applications, and resume upload
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.utils import role_required, allowed_file
from app import db
from app.models import User, StudentProfile, PlacementDrive, Application
import os
from werkzeug.utils import secure_filename
from datetime import date

student_bp = Blueprint('student', __name__, url_prefix='/student')

# Student profile view
@student_bp.route('/profile')
@login_required
@role_required('student')
def profile():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('student/profile.html', profile=profile)

# Edit student profile
@student_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@role_required('student')
def edit_profile():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        profile.full_name = request.form['full_name']
        profile.department = request.form['department']
        profile.year = request.form.get('year')
        profile.cgpa = request.form.get('cgpa') or None
        profile.tenth_marks = request.form.get('tenth_marks') or None
        profile.twelfth_marks = request.form.get('twelfth_marks') or None
        profile.phone = request.form.get('phone')
        profile.address = request.form.get('address')
        profile.skills = request.form.get('skills')
        dob = request.form.get('dob')
        if dob:
            from datetime import datetime
            profile.dob = datetime.strptime(dob, '%Y-%m-%d').date()
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('student.profile'))
    return render_template('student/edit_profile.html', profile=profile)

# Download resume
@student_bp.route('/profile/resume')
@login_required
@role_required('student')
def download_resume():
    from flask import send_from_directory
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if profile and profile.resume_filename:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], profile.resume_filename)
    flash('No resume found.', 'warning')
    return redirect(url_for('student.profile'))

# Student dashboard
@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    total_apps = Application.query.filter_by(student_id=profile.id).count()
    selected = Application.query.filter_by(student_id=profile.id, status='selected').count()
    pending = Application.query.filter_by(student_id=profile.id, status='pending').count()
    return render_template('student/dashboard.html', profile=profile, total_apps=total_apps, selected=selected, pending=pending)

# View approved drives
@student_bp.route('/drives')
@login_required
@role_required('student')
def drives():
    today = date.today()
    drives = PlacementDrive.query.filter_by(is_approved=True, is_active=True).filter(PlacementDrive.application_deadline >= today).all()
    return render_template('student/drives.html', drives=drives)

# View drive details
@student_bp.route('/drives/<int:drive_id>')
@login_required
@role_required('student')
def drive_detail(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if not drive.is_approved or not drive.is_active:
        flash('This drive is not available.', 'warning')
        return redirect(url_for('student.drives'))
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    already_applied = Application.query.filter_by(student_id=profile.id, drive_id=drive_id).first() is not None
    return render_template('student/drive_detail.html', drive=drive, already_applied=already_applied)

# Apply to a drive
@student_bp.route('/drives/<int:drive_id>/apply', methods=['POST'])
@login_required
@role_required('student')
def apply_drive(drive_id):
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)
    # Prevent duplicate applications
    exists = Application.query.filter_by(student_id=profile.id, drive_id=drive_id).first()
    if exists:
        flash('Already applied to this drive.', 'warning')
        return redirect(url_for('student.drives'))
    # Check deadline
    if drive.application_deadline < date.today() or not drive.is_approved or not drive.is_active:
        flash('Drive not open for applications.', 'danger')
        return redirect(url_for('student.drives'))
    app = Application(student_id=profile.id, drive_id=drive_id, status='pending')
    db.session.add(app)
    db.session.commit()
    flash('Application submitted.', 'success')
    return redirect(url_for('student.applications'))

# View application status & history
@student_bp.route('/applications')
@login_required
@role_required('student')
def applications():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    apps = Application.query.filter_by(student_id=profile.id).all()
    return render_template('student/applications.html', applications=apps)

# Withdraw application (only if pending)
@student_bp.route('/applications/<int:app_id>/withdraw', methods=['POST'])
@login_required
@role_required('student')
def withdraw_application(app_id):
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    app = Application.query.get_or_404(app_id)
    # Verify ownership
    if app.student_id != profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('student.applications'))
    # Only pending applications can be withdrawn
    if app.status != 'pending':
        flash('Only pending applications can be withdrawn.', 'warning')
        return redirect(url_for('student.applications'))
    db.session.delete(app)
    db.session.commit()
    flash('Application withdrawn successfully.', 'success')
    return redirect(url_for('student.applications'))

# Resume upload (PDF only)
@student_bp.route('/profile/upload_resume', methods=['POST'])
@login_required
@role_required('student')
def upload_resume():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if 'resume' not in request.files:
        flash('No file part.', 'danger')
        return redirect(url_for('student.dashboard'))
    file = request.files['resume']
    if file.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('student.dashboard'))
    if file and allowed_file(file.filename) and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(f"{profile.roll_number}_resume.pdf")
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        profile.resume_filename = filename
        db.session.commit()
        flash('Resume uploaded.', 'success')
    else:
        flash('Invalid file type. Only PDF allowed.', 'danger')
    return redirect(url_for('student.dashboard'))
