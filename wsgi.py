"""
WSGI Entry Point for ML-Based LMS Intelligence Platform
======================================================

This file serves as the WSGI entry point for deployment platforms.
It imports the Flask app from web_app.py and makes it available as 'application'.
"""

from web_app import app

# WSGI entry point
application = app

if __name__ == "__main__":
    application.run()