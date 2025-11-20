"""Polygon database model."""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.types import TypeDecorator
from app.database import Base
import json
import logging

logger = logging.getLogger(__name__)


class JSONEncodedList(TypeDecorator):
    """Custom type for storing list of points as JSON in database."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert Python list to JSON string for database storage."""
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        """Convert JSON string from database to Python list."""
        if value is None or value.strip() == "":
            return None
        try:
            data = json.loads(value)
            if not isinstance(data, list):
                logger.error(f"Invalid points data structure: expected list, got {type(data).__name__}")
                return []
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in database points column: {value[:100]}...", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Unexpected error deserializing points: {e}", exc_info=True)
            return []


class Polygon(Base):
    """Polygon database entity."""
    __tablename__ = "polygons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    points = Column(JSONEncodedList, nullable=False)

    def __repr__(self):
        return f"<Polygon(id={self.id}, name='{self.name}', points_count={len(self.points) if self.points else 0})>"

    def to_dict(self):
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "points": self.points
        }
