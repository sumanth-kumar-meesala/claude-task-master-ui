"""
Enhanced Projects API endpoints for the new workflow.

This module provides comprehensive project creation and management
endpoints that support the new agent orchestration workflow.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.responses import SuccessResponse, ErrorResponse, CreatedResponse
from app.models.schemas import ProjectCreate, Project
from app.services.enhanced_project_service import EnhancedProjectService
from app.core.exceptions import ValidationException, DatabaseException

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/enhanced-projects", tags=["Enhanced Projects"])

# Service instance
enhanced_project_service = EnhancedProjectService()


@router.post("/", response_model=CreatedResponse)
async def create_comprehensive_project(project_data: ProjectCreate):
    """
    Create a comprehensive project with all required details.
    
    This endpoint captures all project information upfront and validates
    that the project is ready for agent orchestration.
    
    Args:
        project_data: Comprehensive project creation data
        
    Returns:
        Created project with validation status and next steps
        
    Raises:
        HTTPException: If validation fails or database error occurs
    """
    try:
        logger.info(f"Creating comprehensive project: {project_data.name}")
        
        # Create comprehensive project
        result = await enhanced_project_service.create_comprehensive_project(project_data)
        
        return CreatedResponse(
            message="Comprehensive project created successfully",
            data={
                "project": result["project"],
                "validation": result["validation"],
                "ready_for_orchestration": result["ready_for_orchestration"],
                "next_steps": result["next_steps"]
            }
        )
        
    except ValidationException as e:
        logger.warning(f"Project validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project validation failed: {str(e)}"
        )
    except DatabaseException as e:
        logger.error(f"Database error during project creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save project to database"
        )
    except Exception as e:
        logger.error(f"Unexpected error during project creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/{project_id}/orchestration-context", response_model=SuccessResponse)
async def get_orchestration_context(project_id: str):
    """
    Get complete project context for agent orchestration.
    
    This endpoint retrieves all project data and prepares it for
    agent collaboration.
    
    Args:
        project_id: Project ID
        
    Returns:
        Complete project context for orchestration
        
    Raises:
        HTTPException: If project not found or not ready for orchestration
    """
    try:
        logger.info(f"Getting orchestration context for project: {project_id}")
        
        # Get orchestration context
        context = await enhanced_project_service.get_project_for_orchestration(project_id)
        
        return SuccessResponse(
            message="Orchestration context retrieved successfully",
            data=context
        )
        
    except ValueError as e:
        logger.warning(f"Project validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting orchestration context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orchestration context"
        )


@router.post("/{project_id}/validate", response_model=SuccessResponse)
async def validate_project_for_orchestration(project_id: str):
    """
    Validate that a project is ready for agent orchestration.
    
    Args:
        project_id: Project ID to validate
        
    Returns:
        Validation results and recommendations
        
    Raises:
        HTTPException: If project not found
    """
    try:
        logger.info(f"Validating project for orchestration: {project_id}")
        
        # Get project from database
        from app.database.tinydb_handler import get_projects_db
        projects_db = get_projects_db()
        project = projects_db.get_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Create a copy without the id field for validation with ProjectCreate
        project_data_for_validation = {k: v for k, v in project.items() if k not in ['id', 'created_at', 'updated_at', 'session_count']}
        project_data = ProjectCreate(**project_data_for_validation)
        
        # Validate project
        validation_result = await enhanced_project_service._validate_comprehensive_project(project_data)
        
        return SuccessResponse(
            message="Project validation completed",
            data={
                "project_id": project_id,
                "validation": validation_result,
                "ready_for_orchestration": validation_result["is_valid"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate project"
        )


@router.get("/{project_id}/readiness-check", response_model=SuccessResponse)
async def check_orchestration_readiness(project_id: str):
    """
    Check if a project is ready for orchestration and get improvement suggestions.
    
    Args:
        project_id: Project ID to check
        
    Returns:
        Readiness status and improvement suggestions
    """
    try:
        logger.info(f"Checking orchestration readiness for project: {project_id}")
        
        # Get project from database
        from app.database.tinydb_handler import get_projects_db
        projects_db = get_projects_db()
        project = projects_db.get_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Convert to ProjectCreate for validation
        project_data = ProjectCreate(**project)
        
        # Get validation and recommendations
        validation_result = await enhanced_project_service._validate_comprehensive_project(project_data)
        
        # Determine readiness level
        completeness_score = validation_result["completeness_score"]
        if completeness_score >= 80:
            readiness_level = "excellent"
        elif completeness_score >= 60:
            readiness_level = "good"
        elif completeness_score >= 40:
            readiness_level = "fair"
        else:
            readiness_level = "poor"
        
        return SuccessResponse(
            message="Orchestration readiness check completed",
            data={
                "project_id": project_id,
                "readiness_level": readiness_level,
                "completeness_score": completeness_score,
                "is_ready": validation_result["is_valid"],
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"],
                "recommendations": validation_result["recommendations"],
                "next_steps": [
                    "Address validation errors" if validation_result["errors"] else None,
                    "Consider recommendations for better results" if validation_result["warnings"] else None,
                    "Start agent orchestration" if validation_result["is_valid"] else None
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking orchestration readiness: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check orchestration readiness"
        )


@router.patch("/{project_id}/prepare-orchestration", response_model=SuccessResponse)
async def prepare_project_for_orchestration(project_id: str, updates: Dict[str, Any]):
    """
    Update project data to prepare it for orchestration.
    
    Args:
        project_id: Project ID to update
        updates: Project data updates
        
    Returns:
        Updated project and readiness status
    """
    try:
        logger.info(f"Preparing project for orchestration: {project_id}")
        
        # Get project from database
        from app.database.tinydb_handler import get_projects_db
        projects_db = get_projects_db()
        project = projects_db.get_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Update project data
        updated_data = {**project, **updates}
        updated_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Create a copy without system fields for validation with ProjectCreate
        project_data_for_validation = {k: v for k, v in updated_data.items() if k not in ['id', 'created_at', 'updated_at', 'session_count']}
        project_data = ProjectCreate(**project_data_for_validation)
        validation_result = await enhanced_project_service._validate_comprehensive_project(project_data)
        
        # Update readiness flag
        updated_data["is_ready_for_orchestration"] = validation_result["is_valid"]
        
        # Save updated project
        projects_db.update_by_id(project_id, updated_data)
        
        return SuccessResponse(
            message="Project prepared for orchestration",
            data={
                "project": updated_data,
                "validation": validation_result,
                "ready_for_orchestration": validation_result["is_valid"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error preparing project for orchestration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to prepare project for orchestration"
        )


# Health check for enhanced projects service
@router.get("/health", response_model=SuccessResponse)
async def enhanced_projects_health():
    """Health check for enhanced projects service."""
    try:
        # Test database connection
        from app.database.tinydb_handler import get_projects_db
        projects_db = get_projects_db()
        
        # Simple database test
        test_result = projects_db.get_all(limit=1)
        
        return SuccessResponse(
            message="Enhanced projects service is healthy",
            data={
                "service": "enhanced_projects",
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Enhanced projects service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Enhanced projects service is unhealthy"
        )
