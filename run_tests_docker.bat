@echo off
REM Run tests inside Docker container (easiest method)

echo ====================================
echo Polygon Manager - Docker Test Runner
echo ====================================
echo.

echo Building Docker image with test dependencies...
docker-compose build

echo.
echo Running All Tests (API + UI)...
echo ------------------------------------
docker-compose run --rm polygon-backend pytest -v

echo.
echo.
echo Test Summary
echo ------------------------------------
docker-compose run --rm polygon-backend pytest --tb=no -q

echo.
echo ====================================
echo Tests Complete!
echo ====================================
echo.
echo To run tests with coverage:
echo   docker-compose run --rm polygon-backend pytest --cov=app --cov-report=html
echo.
echo To run only API tests:
echo   docker-compose run --rm polygon-backend pytest tests/test_api.py -v
echo.
echo To run only UI tests:
echo   docker-compose run --rm polygon-backend pytest tests/test_ui.py -v
echo.

pause
