"""Repository layer for database operations."""
from sqlalchemy.orm import Session
from app.models.polygon import Polygon
from typing import List, Optional


class PolygonRepository:
    """Repository for Polygon entity operations."""

    @staticmethod
    def find_all(db: Session) -> List[Polygon]:
        """Find all polygons."""
        return db.query(Polygon).all()

    @staticmethod
    def find_by_id(db: Session, polygon_id: int) -> Optional[Polygon]:
        """Find polygon by ID."""
        return db.query(Polygon).filter(Polygon.id == polygon_id).first()

    @staticmethod
    def save(db: Session, polygon: Polygon) -> Polygon:
        """Save polygon to database."""
        db.add(polygon)
        db.commit()
        db.refresh(polygon)
        return polygon

    @staticmethod
    def delete_by_id(db: Session, polygon_id: int) -> int:
        """
        Delete polygon by ID and return count of deleted rows.

        Returns:
            Number of rows deleted (0 or 1)
        """
        result = db.query(Polygon).filter(Polygon.id == polygon_id).delete()
        db.commit()
        return result

    @staticmethod
    def count(db: Session) -> int:
        """Count all polygons."""
        return db.query(Polygon).count()
