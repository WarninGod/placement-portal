"""
Placement Portal Application - Flask App Factory
"""
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import os

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()



def create_app(config_name='default'):
    """
    Flask application factory pattern
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    instance_path = os.path.join(app.root_path, '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.company import company_bp
    from app.student import student_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    # Create tables and default admin
    with app.app_context():
        from app.models import User, CompanyProfile, StudentProfile, PlacementDrive, Application, AdminAction
        db.create_all()
        from app.utils import create_default_admin
        create_default_admin()

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        return """
        <h1>Placement Portal</h1>
        <p>Welcome to the Placement Management System</p>
        <ul>
            <li><a href="/login">Login</a></li>
            <li><a href="/student/register">Student Registration</a></li>
            <li><a href="/company/register">Company Registration</a></li>
        </ul>
        """

    return app
