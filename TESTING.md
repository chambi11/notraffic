# Testing Guide for Polygon Manager

This document describes how to run the tests for the Polygon Manager application.

## Test Structure

The test suite includes:
- **API Tests** (`tests/test_api.py`): 30+ tests covering all API endpoints
- **UI Tests** (`tests/test_ui.py`): 25+ tests covering frontend functionality

## Prerequisites

### For Docker Testing
No additional setup required! The Docker image includes all dependencies and Playwright browsers.

### For Local Testing

#### API Tests Only
```bash
pip install -r requirements.txt
```

#### UI Tests (Additional Setup)
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Running Tests

### ⭐ Easiest Method: Run Tests in Docker (Recommended)

**Windows**:
```bash
run_tests_docker.bat
```

**Linux/Mac**:
```bash
./run_tests_docker.sh
```

**Or manually**:
```bash
# Run API tests only
docker-compose run --rm polygon-backend pytest tests/test_api.py -v

# Run UI tests only
docker-compose run --rm polygon-backend pytest tests/test_ui.py -v

# Run all tests (API + UI)
docker-compose run --rm polygon-backend pytest -v

# Run with coverage
docker-compose run --rm polygon-backend pytest --cov=app --cov-report=html
```

### Alternative: Run Tests Locally

**Prerequisites**:
- Python 3.11 (⚠️ NOT 3.13 - some packages don't have pre-built wheels yet)
- pip

**Install & Run**:
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run API tests
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

**If you get compilation errors**: Use the Docker method instead (easiest).

### Run Tests in Verbose Mode
```bash
pytest -v
```

### Run Specific Test
```bash
pytest tests/test_api.py::TestPolygonAPI::test_create_polygon_success
```

## Test Categories

Tests are marked with categories:
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only UI tests
pytest -m ui

# Skip slow tests
pytest -m "not slow"
```

## Running Tests in Docker

### Build and Run Tests
```bash
# Build the image
docker-compose build

# Run tests in container
docker-compose run polygon-backend pytest

# Run with coverage
docker-compose run polygon-backend pytest --cov=app
```

## API Test Coverage

The API tests cover:
- ✅ Health check endpoint
- ✅ Creating polygons with valid data
- ✅ Creating polygons with minimum points (3)
- ✅ Validation errors (missing name, empty name, whitespace name)
- ✅ Name length validation (max 255 characters)
- ✅ Missing points validation
- ✅ Too few points (less than 3)
- ✅ Invalid point structure
- ✅ NaN and Infinite coordinate handling
- ✅ Coordinate value limits
- ✅ Fetching all polygons
- ✅ Deleting existing polygons
- ✅ Deleting non-existent polygons (404)
- ✅ Invalid ID format handling
- ✅ Data persistence across requests
- ✅ Multiple polygons creation
- ✅ Polygons with many points
- ✅ Response format validation
- ✅ Special characters in names
- ✅ Unicode character support
- ✅ Negative coordinates
- ✅ Decimal coordinate precision

## UI Test Coverage

The UI tests cover:
- ✅ Page loading and title
- ✅ Canvas existence and dimensions (1920x1080)
- ✅ Initial UI state (buttons, inputs)
- ✅ Starting drawing with/without name
- ✅ Canceling drawing
- ✅ Clear canvas functionality
- ✅ Instructions visibility
- ✅ Polygon list section
- ✅ Drawing minimum points requirement (3+)
- ✅ Loading overlay
- ✅ Button styling classes
- ✅ Canvas background image loading
- ✅ CSS and JavaScript loading
- ✅ API URL configuration
- ✅ Console error detection
- ✅ Page layout sections

## Notes for UI Tests

- UI tests automatically start the application via the `live_server` fixture in `conftest.py`
- No manual application startup is required
- The server runs on http://localhost:8080 during UI tests
- UI tests run in headless mode by default (using pytest-playwright)
- To see the browser during tests, use the `--headed` flag:
  ```bash
  pytest tests/test_ui.py --headed
  ```
- To slow down tests for debugging, use `--slowmo`:
  ```bash
  pytest tests/test_ui.py --headed --slowmo 1000
  ```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=app --cov-report=xml
```

## Test Data

- Tests use isolated test databases (temporary SQLite files)
- Each test gets a fresh database
- API delay is disabled during tests for speed
- Sample polygon data is provided via fixtures

## Troubleshooting

### Playwright Installation Issues
```bash
# Reinstall Playwright browsers
playwright install --force chromium
```

### Import Errors
```bash
# Ensure you're in the project root
cd C:\Dev\polygon

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
If UI tests fail because port 8080 is already in use by a manually running instance:
```bash
# Stop any running Docker instances
docker-compose down

# Or stop any local development server
# Then run the tests again
pytest tests/test_ui.py -v
```
The `live_server` fixture in the tests will automatically start the application on port 8080.

## Writing New Tests

### API Test Example
```python
def test_my_feature(client, sample_polygon_data):
    """Test description."""
    response = client.post("/api/polygons", json=sample_polygon_data)
    assert response.status_code == 200
```

### UI Test Example
```python
def test_my_ui_feature(page: Page):
    """Test description."""
    page.goto(BASE_URL)
    button = page.locator("#myButton")
    expect(button).to_be_visible()
```

## Coverage Goals

- **API Tests**: Aim for 90%+ code coverage
- **UI Tests**: Cover all user interactions and UI states
- **Integration**: Ensure end-to-end workflows are tested

Current coverage can be viewed by running:
```bash
pytest --cov=app --cov-report=term-missing
```
