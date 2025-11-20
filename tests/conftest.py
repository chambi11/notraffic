"""
Pytest configuration and fixtures.
"""
import pytest
import os
import tempfile
import threading
import time
import uvicorn
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import app and dependencies
from app.main import app
from app.database.database import Base, get_db
from app.config import settings


@pytest.fixture(scope="function")
def test_db():
    """Create a temporary test database for each test."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    test_database_url = f"sqlite:///{db_path}"

    # Create engine and tables
    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield TestingSessionLocal

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database."""
    def override_get_db():
        try:
            db = test_db()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Temporarily disable the delay for tests
    original_delay = settings.api_delay_seconds
    settings.api_delay_seconds = 0

    with TestClient(app) as test_client:
        yield test_client

    # Restore original delay
    settings.api_delay_seconds = original_delay
    app.dependency_overrides.clear()


@pytest.fixture
def sample_polygon_data():
    """Sample polygon data for testing."""
    return {
        "name": "Test Polygon",
        "points": [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
    }


@pytest.fixture
def sample_triangle_data():
    """Sample triangle data for testing."""
    return {
        "name": "Test Triangle",
        "points": [[0.0, 0.0], [10.0, 0.0], [5.0, 10.0]]
    }


@pytest.fixture(scope="session", autouse=True)
def live_server():
    """
    Start the FastAPI application on a background thread for UI tests.
    This fixture runs automatically for the entire test session.
    """
    # Check if we're running UI tests by looking at test collection
    # Only start server if UI tests are being run
    server_thread = None
    server = None

    def run_server():
        """Run uvicorn server in a thread."""
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=8080,
            log_level="error",  # Minimize logs during tests
            access_log=False
        )
        nonlocal server
        server = uvicorn.Server(config)
        server.run()

    # Start the server in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(2)

    yield

    # Server will stop when the daemon thread is terminated
    if server:
        server.should_exit = True
