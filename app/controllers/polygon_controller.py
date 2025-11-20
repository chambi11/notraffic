"""REST API controller for polygon endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.polygon_schema import CreatePolygonRequest, PolygonResponse, ErrorResponse, DeleteResponse
from app.services.polygon_service import PolygonService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/polygons",
    tags=["polygons"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)


@router.get("", response_model=List[PolygonResponse], status_code=status.HTTP_200_OK)
def get_all_polygons(db: Session = Depends(get_db)):
    """Fetch all polygons."""
    logger.info("GET /api/polygons - Fetching all polygons")
    try:
        polygons = PolygonService.get_all_polygons(db)
        logger.info(f"Successfully fetched {len(polygons)} polygons")
        return polygons
    except Exception as e:
        logger.error(f"Failed to fetch polygons: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch polygons"
        )


@router.post("", response_model=PolygonResponse, status_code=status.HTTP_201_CREATED)
def create_polygon(request: CreatePolygonRequest, db: Session = Depends(get_db)):
    """Create a new polygon."""
    logger.info(f"POST /api/polygons - Creating polygon with name: {request.name}")
    try:
        polygon = PolygonService.create_polygon(db, request.name, request.points)
        logger.info(f"Successfully created polygon with ID: {polygon.id}")
        return polygon
    except ValueError as e:
        logger.warning(f"Invalid polygon creation request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create polygon: {request.name}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create polygon"
        )


@router.delete("/{id}", response_model=DeleteResponse, status_code=status.HTTP_200_OK)
def delete_polygon(id: int, db: Session = Depends(get_db)):
    """Delete a polygon by ID."""
    logger.info(f"DELETE /api/polygons/{id} - Deleting polygon")
    try:
        deleted = PolygonService.delete_polygon(db, id)
        if deleted:
            logger.info(f"Successfully deleted polygon with ID: {id}")
            return {
                "message": "Polygon deleted successfully",
                "id": id
            }
        else:
            logger.warning(f"Polygon not found with ID: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Polygon not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete polygon with ID: {id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete polygon"
        )
