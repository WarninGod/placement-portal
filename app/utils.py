"""
Utility functions and helpers for Placement Portal
Includes admin creation, decorators, and common helpers
"""
from app import db
from app.models import User
from functools import wraps
from flask import session, redirect, url_for, flash, abort


def create_default_admin():
    """
    Creates a default admin user if none exists
    Called automatically when application starts
    This ensures there's always an admin to manage the system
    """
    # Check if any admin user already exists
    admin_exists = User.query.filter_by(role='admin').first()
    
    if not admin_exists:
        # Create default admin user
        admin = User(
            email='admin@placement.com',
            role='admin',
            is_active=True,
            is_approved=True,  # Admin is pre-approved
            is_blacklisted=False
        )
        admin.set_password('admin123')  # Default password (should be changed)
        
        try:
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created successfully")
            print("  Email: admin@placement.com")
            print("  Password: admin123")
            print("  ⚠️  Please change the password after first login!")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating admin user: {e}")


from flask_login import current_user
from flask import abort
def role_required(required_role):
    """Decorator to ensure user has the required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role != required_role:
                abort(403)
            if required_role == 'company' and not current_user.is_approved:
                abort(403)
            if not current_user.is_active_user():
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user():
    """
    Retrieves the current logged-in user from database
    Returns None if no user is logged in
    """
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


def check_application_deadline(deadline_date):
    """
    Checks if application deadline has passed
    Returns True if deadline is still valid, False otherwise
    """
    from datetime import date
    return deadline_date >= date.today()


def allowed_file(filename):
    """
    Checks if uploaded file has an allowed extension
    Used for resume upload validation
    """
    from flask import current_app
    ALLOWED_EXTENSIONS = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def log_admin_action(admin_id, action_type, target_id=None, target_type=None, remarks=None):
    """
    Logs an admin action to the audit trail
    Creates entry in admin_actions table for accountability
    """
    from app.models import AdminAction
    
    action = AdminAction(
        admin_id=admin_id,
        action_type=action_type,
        target_id=target_id,
        target_type=target_type,
        remarks=remarks
    )
    
    try:
        db.session.add(action)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging admin action: {e}")
