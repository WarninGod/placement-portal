"""
Configuration settings for Placement Portal Application
"""
import os

# Get the base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class with common settings"""
    
    # Secret key for session encryption and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-12345'
    
    # Database configuration - SQLite created in instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'placement.db')
    
    # Disable SQLAlchemy modification tracking (saves resources)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads', 'resumes')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    
    # Pagination settings
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
