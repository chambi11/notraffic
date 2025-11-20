"""Polygon service layer with business logic."""
import time
import logging
from typing import List
from sqlalchemy.orm import Session
from app.models.polygon import Polygon
from app.database.repository import PolygonRepository
from app.config import settings

logger = logging.getLogger(__name__)


class PolygonService:
    """Service class for polygon business logic."""

    MAX_NAME_LENGTH = settings.max_name_length
    MAX_POINTS_COUNT = settings.max_points_count
    MAX_COORDINATE = settings.max_coordinate

    @staticmethod
    def _add_delay():
        """Add 5-second delay as per requirements."""
        time.sleep(settings.api_delay_seconds)

    @staticmethod
    def _validate_points(points: List[List[float]]) -> None:
        """
        Validate polygon points for proper format and valid coordinate values.

        Raises:
            ValueError: If validation fails
        """
        if len(points) > PolygonService.MAX_POINTS_COUNT:
            raise ValueError(f"Too many points. Maximum allowed: {PolygonService.MAX_POINTS_COUNT}")

        for point in points:
            if point is None or len(point) != 2:
                raise ValueError("Each point must have exactly 2 coordinates [x, y]")

            for coordinate in point:
                if coordinate is None:
                    raise ValueError("Coordinate cannot be null")
                if not isinstance(coordinate, (int, float)):
                    raise ValueError("Coordinate must be a number")
                if coordinate != coordinate:
                    raise ValueError("Coordinate cannot be NaN")
                if coordinate == float('inf') or coordinate == float('-inf'):
                    raise ValueError("Coordinate cannot be Infinite")
                if abs(coordinate) > PolygonService.MAX_COORDINATE:
                    raise ValueError(f"Coordinate value too large. Maximum allowed: {PolygonService.MAX_COORDINATE}")

    @staticmethod
    def get_all_polygons(db: Session) -> List[Polygon]:
        """Fetch all polygons."""
        logger.debug("Fetching all polygons from database")
        PolygonService._add_delay()
        polygons = PolygonRepository.find_all(db)
        logger.debug(f"Retrieved {len(polygons)} polygons from database")
        return polygons

    @staticmethod
    def create_polygon(db: Session, name: str, points: List[List[float]]) -> Polygon:
        """
        Create a new polygon.

        Args:
            db: Database session
            name: Polygon name
            points: List of points

        Returns:
            Created polygon

        Raises:
            ValueError: If validation fails
        """
        logger.debug(f"Creating polygon: name={name}, pointCount={len(points) if points else 0}")
        PolygonService._add_delay()

        if not name or not name.strip():
            logger.warning("Polygon creation failed: name is required")
            raise ValueError("Polygon name is required")
        if len(name) > PolygonService.MAX_NAME_LENGTH:
            logger.warning(f"Polygon creation failed: name too long (length={len(name)})")
            raise ValueError(f"Polygon name too long. Maximum allowed: {PolygonService.MAX_NAME_LENGTH} characters")

        if not points:
            logger.warning("Polygon creation failed: points are required")
            raise ValueError("Polygon points are required")
        if len(points) < 3:
            logger.warning(f"Polygon creation failed: insufficient points (count={len(points)})")
            raise ValueError("Polygon must have at least 3 points")

        logger.debug(f"Validating {len(points)} points for polygon '{name}'")
        PolygonService._validate_points(points)

        new_polygon = Polygon(id=None, name=name, points=points)
        saved_polygon = PolygonRepository.save(db, new_polygon)
        logger.info(f"Created polygon: id={saved_polygon.id}, name={saved_polygon.name}")
        return saved_polygon

    @staticmethod
    def delete_polygon(db: Session, polygon_id: int) -> bool:
        """
        Delete a polygon by ID.

        Args:
            db: Database session
            polygon_id: ID of polygon to delete

        Returns:
            True if polygon was deleted, False if it didn't exist
        """
        logger.debug(f"Deleting polygon with id={polygon_id}")
        PolygonService._add_delay()

        deleted_count = PolygonRepository.delete_by_id(db, polygon_id)
        deleted = deleted_count > 0

        if deleted:
            logger.info(f"Deleted polygon with id={polygon_id}")
        else:
            logger.debug(f"Polygon not found for deletion: id={polygon_id}")

        return deleted
