"""
Database verification script
Checks tables, relationships, and admin user
"""
from app import create_app, db
from app.models import User, CompanyProfile, StudentProfile, PlacementDrive, Application, AdminAction
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    # Get inspector
    inspector = inspect(db.engine)
    
    print("\n" + "="*60)
    print("  DATABASE VERIFICATION")
    print("="*60)
    
    # List all tables
    print("\n✓ Tables Created:")
    for table_name in inspector.get_table_names():
        print(f"  - {table_name}")
    
    # Check admin user
    print("\n✓ Admin User:")
    admin = User.query.filter_by(role='admin').first()
    if admin:
        print(f"  - Email: {admin.email}")
        print(f"  - Role: {admin.role}")
        print(f"  - Is Active: {admin.is_active}")
        print(f"  - Is Approved: {admin.is_approved}")
    else:
        print("  - No admin user found!")
    
    # Check table columns
    print("\n✓ Table Structures:")
    for table_name in inspector.get_table_names():
        print(f"\n  {table_name.upper()}:")
        columns = inspector.get_columns(table_name)
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"    - {col['name']:20} {str(col['type']):15} {nullable}")
        
        # Show foreign keys
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            print(f"    Foreign Keys:")
            for fk in fks:
                print(f"      → {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
    
    print("\n" + "="*60)
    print("  Database verification complete!")
    print("="*60 + "\n")
