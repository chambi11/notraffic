# Polygon Manager

A web application for managing polygons on an image using Canvas. Users can create, display, and delete polygons by clicking on a background image.

## Features

### Backend (Python FastAPI)
- RESTful API for polygon management
- SQLite database persistence with SQLAlchemy ORM (data persists across restarts)
- 5-second delay on all API operations (as per requirements)
- Comprehensive input validation and error handling
- Transaction-safe operations with proper isolation
- Structured logging framework
- Docker support
- Automatic OpenAPI/Swagger documentation

### Frontend (HTML/CSS/JavaScript)
- Interactive canvas with background image from https://picsum.photos/1920/1080
- Draw polygons by clicking points on the canvas
- Visual representation of all polygons
- Highlight polygons by clicking them in the list
- Delete polygons with confirmation
- Real-time updates and loading indicators

## Quick Start

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- (Optional) Docker and Docker Compose

### Option 1: Run Locally with Python

#### Step 1: Install Dependencies

```bash
# Create and activate virtual environment (recommended)
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Run the Application

```bash
# Run with uvicorn (recommended)
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# OR run directly
python -m app.main
```

#### Step 3: Access the Application

- **Web UI**: http://localhost:8080
- **API Documentation (Swagger)**: http://localhost:8080/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

### Option 2: Run with Docker

#### Step 1: Build and Run

```bash
# Build and start the container
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

#### Step 2: Access the Application

- **Web UI**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs

#### Step 3: Stop the Container

```bash
docker-compose down
```

## API Endpoints

### 1. Get All Polygons
```
GET /api/polygons
```
Returns all saved polygons in the format:
```json
[
  {
    "id": 1,
    "name": "P1",
    "points": [[12.3, 12.0], [16.3, 12.0], [16.3, 8.0], [12.3, 8.0]]
  }
]
```

### 2. Create Polygon
```
POST /api/polygons
Content-Type: application/json

{
  "name": "P1",
  "points": [[12.3, 12.0], [16.3, 12.0], [16.3, 8.0], [12.3, 8.0]]
}
```
Returns the created polygon with assigned ID.

### 3. Delete Polygon
```
DELETE /api/polygons/{id}
```
Deletes the polygon with the specified ID.

## Using the Application

1. **Access the UI**: Open your browser and navigate to http://localhost:8080

2. **Access the API Documentation**: Navigate to http://localhost:8080/docs for interactive API documentation (Swagger UI)

3. **Create a Polygon**:
   - Enter a name for the polygon in the text field
   - Click "Start Drawing"
   - Click on the canvas to add points (minimum 3 points required)
   - Click "Finish Polygon" to save (note: this will take 5 seconds due to the API delay)

4. **View Polygons**:
   - All polygons are listed on the right side
   - Saved polygons are displayed on the canvas with green outlines
   - The currently drawing polygon is shown in blue

5. **Highlight Polygons**:
   - Click on a polygon in the list to highlight it (red outline on canvas)
   - Click again to remove the highlight

6. **Delete Polygons**:
   - Click the "Delete Polygon" button on any polygon in the list
   - Confirm the deletion
   - Note: Deletion takes 5 seconds due to the API delay

7. **Clear Highlights**:
   - Click "Clear Canvas" to remove all highlights

## Project Structure

```
polygon/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                  # Application configuration
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── polygon_controller.py        # REST API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── polygon_service.py           # Business logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── polygon.py                   # Polygon model (SQLAlchemy)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── polygon_schema.py            # Request/Response schemas (Pydantic)
│   └── database/
│       ├── __init__.py
│       ├── database.py                  # Database configuration
│       └── repository.py                # Database operations
├── src/main/resources/static/           # Frontend files
│   ├── index.html                       # Main HTML page
│   ├── styles.css                       # CSS styles
│   └── app.js                           # JavaScript logic
├── requirements.txt                     # Python dependencies
├── Dockerfile                           # Docker configuration
├── docker-compose.yml                   # Docker Compose configuration
├── .dockerignore                        # Docker ignore file
└── .gitignore                          # Git ignore file
```

## Data Persistence

Polygons are stored in a **SQLite database** using SQLAlchemy ORM.
The database file is created in the `data/` directory and persists across restarts.

### Database Features:
- **SQLite file-based database** (`sqlite:///./data/polygon.db`)
- **SQLAlchemy ORM** for object-relational mapping
- **JSON storage** for polygon points using custom type converter
- **Automatic schema generation** via SQLAlchemy Base.metadata.create_all()
- **Transaction-safe operations** with proper isolation

### About Persistence
The SQLite database stores data persistently in the `data/` directory.
This ensures all polygons are preserved even after the application restarts.

## Technical Details

- **Backend Framework**: FastAPI 0.104.1
- **Python Version**: 3.11+
- **ASGI Server**: Uvicorn
- **Database**: SQLite (embedded, file-based)
- **ORM**: SQLAlchemy 2.0.23
- **Validation**: Pydantic 2.5.0
- **Logging**: Python logging with structured format
- **Frontend**: Vanilla JavaScript (ES6+), HTML5 Canvas
- **Containerization**: Docker with multi-stage builds
- **JSON Processing**: Native Python json module

## API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

## Configuration

Application settings can be configured via environment variables or `.env` file:

```bash
# Application settings
APP_NAME=polygon-manager
APP_HOST=0.0.0.0
APP_PORT=8080

# Database
DATABASE_URL=sqlite:///./data/polygon.db
DATABASE_ECHO=false

# Validation
MAX_COORDINATE=1000000.0
MAX_NAME_LENGTH=255
MAX_POINTS_COUNT=10000

# API delay (seconds)
API_DELAY_SECONDS=5

# Logging
LOG_LEVEL=INFO
```

## Testing

### Running Tests with Docker (Recommended)

The recommended way to run tests is using Docker, which ensures a consistent environment:

**Windows:**
```bash
run_tests_docker.bat
```

**Linux/Mac:**
```bash
./run_tests_docker.sh
```

This runs the full test suite with pytest and generates a coverage report.

### Running Tests Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for UI tests)
playwright install chromium

# Run all tests
pytest -v

# Run only API tests
pytest tests/test_api.py -v

# Run only UI tests (app auto-starts via live_server fixture)
pytest tests/test_ui.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Test Coverage

The test suite includes comprehensive validation of:
- **API Tests**: 30+ tests covering all endpoints, validation, error handling, and persistence
- **UI Tests**: 25+ tests covering frontend functionality, canvas drawing, and user interactions
- **Coverage**: 82% code coverage across all modules

For detailed testing information, see [TESTING.md](TESTING.md).

## Notes

- All API operations include a 5-second delay as specified in the requirements
- The canvas background image is loaded from https://picsum.photos/1920/1080
- CORS is enabled to allow frontend-backend communication
- The application serves static files from the `src/main/resources/static` directory
- Database file is stored in `data/polygon.db` with automatic creation
- API documentation is automatically generated and available at `/docs`

## Development

### Installing development dependencies
```bash
pip install -r requirements.txt
```

### Running in development mode
```bash
# With auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Code formatting (optional)
```bash
# Install black and flake8
pip install black flake8

# Format code
black app/

# Lint code
flake8 app/
```

## License

This project is provided as-is for demonstration purposes.
