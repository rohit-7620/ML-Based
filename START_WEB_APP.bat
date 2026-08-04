@echo off
echo ========================================
echo  ML-Based LMS Intelligence Platform
echo  Starting Web Application...
echo ========================================
echo.

REM Check if models exist
if not exist "models\grading\metadata.json" (
    echo Models not found. Training models first...
    python run_pipeline_with_persistence.py --train
    echo.
)

echo Starting web server...
echo.
echo Web application will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python web_app.py

pause
