"""
Admin routes for Placement Portal
Handles dashboard, approvals, blacklisting, and data views
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils import role_required, log_admin_action
from app import db
from app.models import User, CompanyProfile, StudentProfile, PlacementDrive, Application

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin dashboard with statistics
@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    stats = {
        'students': User.query.filter_by(role='student').count(),
        'companies': User.query.filter_by(role='company').count(),
        'pending_companies': User.query.filter_by(role='company', is_approved=False).count(),
        'pending_drives': PlacementDrive.query.filter_by(is_approved=False).count(),
        'active_drives': PlacementDrive.query.filter_by(is_approved=True, is_active=True).count(),
        'applications': Application.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats)

# List and approve/reject companies
@admin_bp.route('/companies')
@login_required
@role_required('admin')
def companies():
    q = request.args.get('q', '')
    query = User.query.filter_by(role='company')
    if q:
        query = query.join(CompanyProfile).filter(CompanyProfile.company_name.ilike(f'%{q}%'))
    companies = query.all()
    return render_template('admin/companies.html', companies=companies, q=q)

# Company detail view
@admin_bp.route('/companies/<int:user_id>')
@login_required
@role_required('admin')
def company_detail(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'company':
        flash('Invalid company.', 'danger')
        return redirect(url_for('admin.companies'))
    company = CompanyProfile.query.filter_by(user_id=user_id).first()
    drives = PlacementDrive.query.filter_by(company_id=company.id).all() if company else []
    total_applications = Application.query.join(PlacementDrive).filter(PlacementDrive.company_id == company.id).count() if company else 0
    return render_template('admin/company_detail.html', user=user, company=company, drives=drives, total_applications=total_applications)

@admin_bp.route('/companies/pending')
@login_required
@role_required('admin')
def pending_companies():
    companies = User.query.filter_by(role='company', is_approved=False).all()
    return render_template('admin/pending_companies.html', companies=companies)

@admin_bp.route('/companies/<int:user_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_company(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    log_admin_action(current_user.id, 'approve_company', user_id, 'company')
    flash('Company approved.', 'success')
    return redirect(url_for('admin.pending_companies'))

@admin_bp.route('/companies/<int:user_id>/reject', methods=['POST'])
@login_required
@role_required('admin')
def reject_company(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    log_admin_action(current_user.id, 'reject_company', user_id, 'company')
    flash('Company rejected and deleted.', 'info')
    return redirect(url_for('admin.pending_companies'))

@admin_bp.route('/companies/<int:user_id>/blacklist', methods=['POST'])
@login_required
@role_required('admin')
def blacklist_company(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    log_admin_action(current_user.id, 'blacklist_company', user_id, 'company')
    flash('Company blacklist status changed.', 'info')
    return redirect(url_for('admin.companies'))

# List and approve/reject placement drives
@admin_bp.route('/drives')
@login_required
@role_required('admin')
def drives():
    q = request.args.get('q', '')
    query = PlacementDrive.query
    if q:
        query = query.filter(PlacementDrive.title.ilike(f'%{q}%'))
    drives = query.all()
    return render_template('admin/drives.html', drives=drives, q=q)

@admin_bp.route('/drives/pending')
@login_required
@role_required('admin')
def pending_drives():
    drives = PlacementDrive.query.filter_by(is_approved=False).all()
    return render_template('admin/pending_drives.html', drives=drives)

@admin_bp.route('/drives/<int:drive_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.is_approved = True
    db.session.commit()
    log_admin_action(current_user.id, 'approve_drive', drive_id, 'drive')
    flash('Drive approved.', 'success')
    return redirect(url_for('admin.pending_drives'))

@admin_bp.route('/drives/<int:drive_id>/reject', methods=['POST'])
@login_required
@role_required('admin')
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    db.session.delete(drive)
    db.session.commit()
    log_admin_action(current_user.id, 'reject_drive', drive_id, 'drive')
    flash('Drive rejected and deleted.', 'info')
    return redirect(url_for('admin.pending_drives'))

# View, search, and blacklist students
@admin_bp.route('/students')
@login_required
@role_required('admin')
def students():
    q = request.args.get('q', '')
    query = User.query.filter_by(role='student')
    if q:
        query = query.join(StudentProfile).filter(StudentProfile.full_name.ilike(f'%{q}%'))
    students = query.all()
    return render_template('admin/students.html', students=students, q=q)

# Student detail view
@admin_bp.route('/students/<int:user_id>')
@login_required
@role_required('admin')
def student_detail(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'student':
        flash('Invalid student.', 'danger')
        return redirect(url_for('admin.students'))
    student = StudentProfile.query.filter_by(user_id=user_id).first()
    applications = Application.query.filter_by(student_id=student.id).all() if student else []
    return render_template('admin/student_detail.html', user=user, student=student, applications=applications)

@admin_bp.route('/students/<int:user_id>/blacklist', methods=['POST'])
@login_required
@role_required('admin')
def blacklist_student(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    log_admin_action(current_user.id, 'blacklist_student', user_id, 'student')
    flash('Student blacklist status changed.', 'info')
    return redirect(url_for('admin.students'))

# View all applications
@admin_bp.route('/applications')
@login_required
@role_required('admin')
def applications():
    q = request.args.get('q', '')
    query = Application.query
    if q:
        query = query.join(StudentProfile).filter(StudentProfile.full_name.ilike(f'%{q}%'))
    applications = query.all()
    return render_template('admin/applications.html', applications=applications, q=q)

# Close a drive (admin action)
@admin_bp.route('/drives/<int:drive_id>/close', methods=['POST'])
@login_required
@role_required('admin')
def close_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.is_active = False
    db.session.commit()
    log_admin_action(current_user.id, 'close_drive', drive_id, 'drive')
    flash('Drive closed.', 'info')
    return redirect(url_for('admin.drives'))

# Statistics page
@admin_bp.route('/statistics')
@login_required
@role_required('admin')
def statistics():
    from app.models import AdminAction
    from sqlalchemy import func
    
    # Basic stats
    stats = {
        'total_students': User.query.filter_by(role='student').count(),
        'total_companies': User.query.filter_by(role='company').count(),
        'active_drives': PlacementDrive.query.filter_by(is_approved=True, is_active=True).count(),
        'total_applications': Application.query.count(),
        'pending': Application.query.filter_by(status='pending').count(),
        'shortlisted': Application.query.filter_by(status='shortlisted').count(),
        'selected': Application.query.filter_by(status='selected').count(),
        'rejected': Application.query.filter_by(status='rejected').count(),
    }
    total = stats['total_applications']
    stats['success_rate'] = round((stats['selected'] / total * 100), 1) if total > 0 else 0
    
    # Top companies by applications
    top_companies_query = db.session.query(
        CompanyProfile.company_name,
        func.count(Application.id).label('app_count')
    ).join(PlacementDrive, PlacementDrive.company_id == CompanyProfile.id
    ).join(Application, Application.drive_id == PlacementDrive.id
    ).group_by(CompanyProfile.company_name
    ).order_by(func.count(Application.id).desc()
    ).limit(5).all()
    
    top_companies = [{'name': c[0], 'count': c[1]} for c in top_companies_query]
    
    # Department-wise stats
    dept_stats_query = db.session.query(
        StudentProfile.department,
        func.count(StudentProfile.id).label('student_count')
    ).group_by(StudentProfile.department).all()
    
    dept_stats = []
    for dept, count in dept_stats_query:
        apps = db.session.query(func.count(Application.id)).join(
            StudentProfile, StudentProfile.id == Application.student_id
        ).filter(StudentProfile.department == dept).scalar() or 0
        selected = db.session.query(func.count(Application.id)).join(
            StudentProfile, StudentProfile.id == Application.student_id
        ).filter(StudentProfile.department == dept, Application.status == 'selected').scalar() or 0
        dept_stats.append({'name': dept or 'Unknown', 'students': count, 'applications': apps, 'selected': selected})
    
    # Recent admin actions
    recent_actions = AdminAction.query.order_by(AdminAction.timestamp.desc()).limit(10).all()
    
    return render_template('admin/statistics.html', 
                           stats=stats, 
                           top_companies=top_companies,
                           dept_stats=dept_stats,
                           recent_actions=recent_actions)

# Export students to CSV
@admin_bp.route('/export/students')
@login_required
@role_required('admin')
def export_students():
    import csv
    from io import StringIO
    from flask import Response
    
    students = StudentProfile.query.all()
    
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Full Name', 'Roll Number', 'Department', 'CGPA', 'Email', 'Phone'])
    
    for s in students:
        user = User.query.get(s.user_id)
        writer.writerow([s.id, s.full_name, s.roll_number, s.department, s.cgpa, user.email if user else '', s.phone or ''])
    
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=students.csv'})

# Export applications to CSV
@admin_bp.route('/export/applications')
@login_required
@role_required('admin')
def export_applications():
    import csv
    from io import StringIO
    from flask import Response
    
    applications = Application.query.all()
    
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Student Name', 'Roll Number', 'Drive Title', 'Company', 'Status', 'Applied At'])
    
    for app in applications:
        writer.writerow([
            app.id,
            app.student.full_name if app.student else '',
            app.student.roll_number if app.student else '',
            app.drive.title if app.drive else '',
            app.drive.company.company_name if app.drive and app.drive.company else '',
            app.status,
            app.applied_at.strftime('%Y-%m-%d %H:%M') if app.applied_at else ''
        ])
    
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=applications.csv'})

# Export companies to CSV
@admin_bp.route('/export/companies')
@login_required
@role_required('admin')
def export_companies():
    import csv
    from io import StringIO
    from flask import Response
    
    companies = CompanyProfile.query.all()
    
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Company Name', 'Industry', 'Location', 'Email', 'Contact Person', 'Status'])
    
    for c in companies:
        user = User.query.get(c.user_id)
        status = 'Approved' if user and user.is_approved else 'Pending'
        if user and user.is_blacklisted:
            status = 'Blacklisted'
        writer.writerow([c.id, c.company_name, c.industry or '', c.location or '', user.email if user else '', c.contact_person or '', status])
    
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=companies.csv'})
