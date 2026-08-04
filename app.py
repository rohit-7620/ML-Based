"""
Main Entry Point for ML-Based LMS Intelligence Platform
=======================================================

This file serves as the main application entry point for deployment platforms
that look for app.py as the default Flask application file.
"""

# Import the main Flask app from web_app
from web_app import app

# Make the app available at module level
application = app

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)