"""
Application entry point
Run this file to start the Flask development server
"""
from app import create_app

# Create Flask application instance
app = create_app('development')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  PLACEMENT PORTAL APPLICATION")
    print("="*60)
    print("  Starting development server...")
    print("  Default Admin Credentials:")
    print("    Email: admin@placement.com")
    print("    Password: admin123")
    print("="*60 + "\n")
    
    # Run Flask development server
    app.run(debug=True, host='127.0.0.1', port=5000)
