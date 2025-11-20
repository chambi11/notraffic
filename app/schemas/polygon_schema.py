"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, field_validator
from typing import List
import math


class CreatePolygonRequest(BaseModel):
    """Request schema for creating a polygon."""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the polygon")
    points: List[List[float]] = Field(..., min_length=3, description="List of points, each point is [x, y]")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate name is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError("Polygon name is required")
        if len(v) > 255:
            raise ValueError(f"Polygon name too long. Maximum allowed: 255 characters")
        return v

    @field_validator('points')
    @classmethod
    def validate_points(cls, v):
        """Validate that each point has exactly 2 coordinates and valid values."""
        if not v:
            raise ValueError("Points are required")
        if len(v) < 3:
            raise ValueError("Polygon must have at least 3 points")
        for i, point in enumerate(v):
            if len(point) != 2:
                raise ValueError("Each point must have exactly 2 coordinates [x, y]")
            for j, coord in enumerate(point):
                if not isinstance(coord, (int, float)):
                    raise ValueError("Coordinate must be a number")
                if math.isnan(coord):
                    raise ValueError("Coordinate cannot be NaN")
                if math.isinf(coord):
                    raise ValueError("Coordinate cannot be Infinite")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "P1",
                    "points": [[12.3, 12.0], [16.3, 12.0], [16.3, 8.0], [12.3, 8.0]]
                }
            ]
        }
    }


class PolygonResponse(BaseModel):
    """Response schema for polygon."""
    id: int
    name: str
    points: List[List[float]]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "P1",
                    "points": [[12.3, 12.0], [16.3, 12.0], [16.3, 8.0], [12.3, 8.0]]
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "Polygon not found"
                }
            ]
        }
    }


class DeleteResponse(BaseModel):
    """Response schema for delete operations."""
    message: str
    id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Polygon deleted successfully",
                    "id": 1
                }
            ]
        }
    }
