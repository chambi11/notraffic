@echo off
REM Script to run tests for Polygon Manager (Windows)

echo ====================================
echo Polygon Manager - Test Runner
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo Running API Tests...
echo ------------------------------------
pytest tests/test_api.py -v

echo.
echo Test Summary
echo ------------------------------------
pytest tests/test_api.py --tb=no -q

echo.
echo To run UI tests, ensure the application is running and execute:
echo   pytest tests/test_ui.py
echo.
echo To run all tests with coverage:
echo   pytest --cov=app --cov-report=html

pause
