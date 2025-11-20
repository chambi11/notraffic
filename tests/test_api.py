"""
API endpoint tests for Polygon Manager.
Tests all CRUD operations, validation, and error handling.
"""
import pytest
import time


class TestPolygonAPI:
    """Test suite for polygon API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_get_empty_polygons(self, client):
        """Test fetching polygons when database is empty."""
        response = client.get("/api/polygons")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_polygon_success(self, client, sample_polygon_data):
        """Test creating a valid polygon."""
        response = client.post("/api/polygons", json=sample_polygon_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == sample_polygon_data["name"]
        assert data["points"] == sample_polygon_data["points"]
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_create_triangle(self, client, sample_triangle_data):
        """Test creating a triangle (minimum 3 points)."""
        response = client.post("/api/polygons", json=sample_triangle_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == sample_triangle_data["name"]
        assert len(data["points"]) == 3

    def test_create_polygon_missing_name(self, client):
        """Test creating polygon without name."""
        data = {"points": [[0.0, 0.0], [10.0, 0.0], [5.0, 10.0]]}
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 422  # Validation error

    def test_create_polygon_empty_name(self, client):
        """Test creating polygon with empty name."""
        data = {"name": "", "points": [[0.0, 0.0], [10.0, 0.0], [5.0, 10.0]]}
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 422
        detail_str = str(response.json()["detail"]).lower()
        assert "at least 1 character" in detail_str or "name" in detail_str

    def test_create_polygon_whitespace_name(self, client):
        """Test creating polygon with whitespace-only name."""
        data = {"name": "   ", "points": [[0.0, 0.0], [10.0, 0.0], [5.0, 10.0]]}
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 422
        assert "name is required" in str(response.json()["detail"]).lower()

    def test_create_polygon_name_too_long(self, client):
        """Test creating polygon with name exceeding max length."""
        data = {
            "name": "A" * 256,  # Max is 255
            "points": [[0.0, 0.0], [10.0, 0.0], [5.0, 10.0]]
        }
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 422
        detail_str = str(response.json()["detail"]).lower()
        assert "255" in detail_str or "too long" in detail_str

    def test_create_polygon_missing_points(self, client):
        """Test creating polygon without points."""
        data = {"name": "Test"}
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 422  # Validation error

    def test_create_polygon_too_few_points(self, client):
        """Test creating polygon with less than 3 points."""
        data = {"name": "Test", "points": [[0.0, 0.0], [10.0, 0.0]]}
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 422
        detail_str = str(response.json()["detail"]).lower()
        assert "at least 3" in detail_str or "3 items" in detail_str

    def test_create_polygon_invalid_point_structure(self, client):
        """Test creating polygon with invalid point structure."""
        data = {"name": "Test", "points": [[0.0, 0.0], [10.0], [5.0, 10.0]]}
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 422
        assert "2 coordinates" in str(response.json()["detail"]).lower()

    def test_create_polygon_nan_coordinate(self, client):
        """Test creating polygon with NaN coordinate."""
        import json
        # NaN cannot be sent via standard JSON, so we test that it's rejected
        # We'll send a string representation and verify backend rejects it
        data = {"name": "Test", "points": [[0.0, 0.0], ["NaN", 0.0], [5.0, 10.0]]}
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 422  # Should be rejected by Pydantic

    def test_create_polygon_infinite_coordinate(self, client):
        """Test creating polygon with infinite coordinate."""
        # Infinity cannot be sent via standard JSON, so we send a very large number
        # that exceeds our coordinate limit
        data = {"name": "Test", "points": [[0.0, 0.0], [1e15, 0.0], [5.0, 10.0]]}
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 400  # Should be rejected by service layer

    def test_create_polygon_coordinate_too_large(self, client):
        """Test creating polygon with coordinate exceeding max value."""
        data = {"name": "Test", "points": [[0.0, 0.0], [1e10, 0.0], [5.0, 10.0]]}
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()

    def test_get_all_polygons(self, client, sample_polygon_data, sample_triangle_data):
        """Test fetching all polygons."""
        # Create two polygons
        client.post("/api/polygons", json=sample_polygon_data)
        client.post("/api/polygons", json=sample_triangle_data)

        # Fetch all
        response = client.get("/api/polygons")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == sample_polygon_data["name"]
        assert data[1]["name"] == sample_triangle_data["name"]

    def test_delete_polygon_success(self, client, sample_polygon_data):
        """Test deleting an existing polygon."""
        # Create polygon
        create_response = client.post("/api/polygons", json=sample_polygon_data)
        polygon_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/polygons/{polygon_id}")
        assert response.status_code == 200

        # Verify it's gone
        get_response = client.get("/api/polygons")
        assert len(get_response.json()) == 0

    def test_delete_nonexistent_polygon(self, client):
        """Test deleting a polygon that doesn't exist."""
        response = client.delete("/api/polygons/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_invalid_id(self, client):
        """Test deleting with invalid ID format."""
        response = client.delete("/api/polygons/invalid")
        assert response.status_code == 422

    def test_polygon_persistence(self, client, sample_polygon_data):
        """Test that polygons persist across requests."""
        # Create polygon
        create_response = client.post("/api/polygons", json=sample_polygon_data)
        polygon_id = create_response.json()["id"]

        # Fetch it in separate request
        get_response = client.get("/api/polygons")
        assert len(get_response.json()) == 1
        assert get_response.json()[0]["id"] == polygon_id

    def test_multiple_polygons_different_names(self, client):
        """Test creating multiple polygons with different names."""
        polygons = [
            {"name": f"Polygon {i}", "points": [[0, 0], [10, 0], [5, 10]]}
            for i in range(5)
        ]

        for poly_data in polygons:
            response = client.post("/api/polygons", json=poly_data)
            assert response.status_code == 201

        # Verify all created
        response = client.get("/api/polygons")
        assert len(response.json()) == 5

    def test_polygon_with_many_points(self, client):
        """Test creating polygon with many points (but under limit)."""
        points = [[float(i), float(i)] for i in range(100)]
        data = {"name": "Large Polygon", "points": points}

        response = client.post("/api/polygons", json=data)
        assert response.status_code == 201
        assert len(response.json()["points"]) == 100

    def test_polygon_response_format(self, client, sample_polygon_data):
        """Test that response format matches specification."""
        response = client.post("/api/polygons", json=sample_polygon_data)
        data = response.json()

        # Verify required fields
        assert "id" in data
        assert "name" in data
        assert "points" in data

        # Verify types
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["points"], list)

        # Verify points structure
        for point in data["points"]:
            assert isinstance(point, list)
            assert len(point) == 2
            assert isinstance(point[0], (int, float))
            assert isinstance(point[1], (int, float))

    def test_api_delay_disabled_for_tests(self, client, sample_polygon_data):
        """Test that API delay is disabled during tests."""
        start_time = time.time()
        client.post("/api/polygons", json=sample_polygon_data)
        elapsed = time.time() - start_time

        # Should complete in less than 1 second (much less than 5 second delay)
        assert elapsed < 1.0

    def test_create_polygon_special_characters_in_name(self, client):
        """Test creating polygon with special characters in name."""
        data = {
            "name": "Test @ # $ % & * () [] {}",
            "points": [[0.0, 0.0], [10.0, 0.0], [5.0, 10.0]]
        }
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 201

    def test_create_polygon_unicode_name(self, client):
        """Test creating polygon with Unicode characters in name."""
        data = {
            "name": "多边形 🔺 Polygon",
            "points": [[0.0, 0.0], [10.0, 0.0], [5.0, 10.0]]
        }
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 201
        assert response.json()["name"] == data["name"]

    def test_create_polygon_negative_coordinates(self, client):
        """Test creating polygon with negative coordinates."""
        data = {
            "name": "Negative Coords",
            "points": [[-10.0, -10.0], [10.0, -10.0], [0.0, 10.0]]
        }
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 201

    def test_create_polygon_decimal_coordinates(self, client):
        """Test creating polygon with decimal coordinates."""
        data = {
            "name": "Decimal Coords",
            "points": [[1.5, 2.7], [3.14, 2.71], [0.5, 4.9]]
        }
        response = client.post("/api/polygons", json=data)
        assert response.status_code == 201

        # Verify decimal precision is preserved
        result_points = response.json()["points"]
        assert result_points[0][0] == 1.5
        assert result_points[0][1] == 2.7
