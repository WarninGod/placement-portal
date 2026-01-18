"""
Company routes for Placement Portal
Profile, drive management, and application review
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils import role_required
from app import db
from app.models import User, CompanyProfile, PlacementDrive, Application, StudentProfile
from datetime import date

company_bp = Blueprint('company', __name__, url_prefix='/company')

# Company dashboard
@company_bp.route('/dashboard')
@login_required
@role_required('company')
def dashboard():
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drives = PlacementDrive.query.filter_by(company_id=profile.id).all() if profile else []
    stats = {
        'total_drives': len(drives),
        'active_drives': len([d for d in drives if d.is_active and d.is_approved]),
        'pending_drives': len([d for d in drives if not d.is_approved]),
        'total_applications': Application.query.join(PlacementDrive).filter(PlacementDrive.company_id == profile.id).count() if profile else 0
    }
    return render_template('company/dashboard.html', profile=profile, drives=drives, stats=stats)

# Company profile view
@company_bp.route('/profile')
@login_required
@role_required('company')
def profile():
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('company/profile.html', profile=profile)

# Edit company profile
@company_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@role_required('company')
def edit_profile():
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        profile.company_name = request.form['company_name']
        profile.industry = request.form.get('industry')
        profile.location = request.form.get('location')
        profile.website = request.form.get('website')
        profile.contact_person = request.form.get('contact_person')
        profile.contact_phone = request.form.get('contact_phone')
        profile.description = request.form.get('description')
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('company.profile'))
    return render_template('company/edit_profile.html', profile=profile)

# Download student resume (for company reviewing applications)
@company_bp.route('/resume/<int:student_id>')
@login_required
@role_required('company')
def download_resume(student_id):
    from flask import send_from_directory, current_app
    student = StudentProfile.query.get_or_404(student_id)
    if student.resume_filename:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], student.resume_filename)
    flash('Resume not found.', 'warning')
    return redirect(url_for('company.drives'))

# Create placement drive (only if approved)
@company_bp.route('/drives/create', methods=['GET', 'POST'])
@login_required
@role_required('company')
def create_drive():
    if not current_user.is_approved:
        flash('Company not approved yet.', 'warning')
        return redirect(url_for('company.profile'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        job_type = request.form['job_type']
        location = request.form['location']
        package = request.form['package']
        eligibility_criteria = request.form['eligibility_criteria']
        required_skills = request.form['required_skills']
        application_deadline_str = request.form['application_deadline']
        # Convert string to date object
        from datetime import datetime
        application_deadline = datetime.strptime(application_deadline_str, '%Y-%m-%d').date()
        drive = PlacementDrive(
            company_id=current_user.company_profile.id,
            title=title,
            description=description,
            job_type=job_type,
            location=location,
            package=package,
            eligibility_criteria=eligibility_criteria,
            required_skills=required_skills,
            application_deadline=application_deadline,
            is_approved=False,
            is_active=True
        )
        db.session.add(drive)
        db.session.commit()
        flash('Drive created. Awaiting admin approval.', 'info')
        return redirect(url_for('company.drives'))
    return render_template('company/create_drive.html')

# List, edit, and close drives
@company_bp.route('/drives')
@login_required
@role_required('company')
def drives():
    drives = PlacementDrive.query.filter_by(company_id=current_user.company_profile.id).all()
    return render_template('company/drives.html', drives=drives)

@company_bp.route('/drives/<int:drive_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('company')
def edit_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.company_profile.id or not drive.is_active:
        flash('Unauthorized or drive closed.', 'danger')
        return redirect(url_for('company.drives'))
    if request.method == 'POST':
        drive.title = request.form['title']
        drive.description = request.form['description']
        drive.job_type = request.form['job_type']
        drive.location = request.form['location']
        drive.package = request.form['package']
        drive.eligibility_criteria = request.form['eligibility_criteria']
        drive.required_skills = request.form['required_skills']
        # Convert string to date object
        from datetime import datetime
        application_deadline_str = request.form['application_deadline']
        drive.application_deadline = datetime.strptime(application_deadline_str, '%Y-%m-%d').date()
        db.session.commit()
        flash('Drive updated.', 'success')
        return redirect(url_for('company.drives'))
    return render_template('company/edit_drive.html', drive=drive)

@company_bp.route('/drives/<int:drive_id>/close', methods=['POST'])
@login_required
@role_required('company')
def close_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.company_profile.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.drives'))
    drive.is_active = False
    db.session.commit()
    flash('Drive closed.', 'info')
    return redirect(url_for('company.drives'))

# View student applications for a drive
@company_bp.route('/drives/<int:drive_id>/applications')
@login_required
@role_required('company')
def drive_applications(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.company_profile.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.drives'))
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template('company/drive_applications.html', drive=drive, applications=applications)

# Update application status
@company_bp.route('/applications/<int:app_id>/update', methods=['POST'])
@login_required
@role_required('company')
def update_application(app_id):
    app = Application.query.get_or_404(app_id)
    drive = PlacementDrive.query.get(app.drive_id)
    if drive.company_id != current_user.company_profile.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.drives'))
    status = request.form['status']
    if status in ['pending', 'shortlisted', 'selected', 'rejected']:
        app.status = status
        db.session.commit()
        flash('Application status updated.', 'success')
    else:
        flash('Invalid status.', 'danger')
    return redirect(url_for('company.drive_applications', drive_id=app.drive_id))
