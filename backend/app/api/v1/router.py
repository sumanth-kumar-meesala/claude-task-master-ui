"""
Main API router for version 1.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any, Optional
import time
import logging
import json
import asyncio
from datetime import datetime

from app.core.config import get_settings
from app.database.tinydb_handler import get_projects_db, get_templates_db
from app.api.v1.chat import router as chat_router
from app.api.v1.project_files import router as project_files_router
from app.api.v1.enhanced_projects import router as enhanced_projects_router
from app.api.v1.file_management import router as file_management_router
from app.api.v1.task_generation import router as task_generation_router

settings = get_settings()
logger = logging.getLogger(__name__)

# Create API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(chat_router)
api_router.include_router(project_files_router)
api_router.include_router(enhanced_projects_router)
api_router.include_router(file_management_router)
api_router.include_router(task_generation_router)





@api_router.get("/", tags=["API Info"])
async def api_info():
    """Get API version information."""
    return {
        "api_version": "v1",
        "service": "Project Overview Agent API",
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
        "endpoints": {
            "projects": "/projects",
            "templates": "/templates",
            "project_files": "/project-files",
            "task_generation": "/task-generation",
        }
    }


@api_router.get("/status", tags=["Status"])
async def api_status():
    """Get API status and health information."""
    try:
        # Check database connections
        projects_db = get_projects_db()
        templates_db = get_templates_db()
        from app.database.tinydb_handler import get_project_files_db
        project_files_db = get_project_files_db()

        # Get database stats
        projects_count = projects_db.count()
        templates_count = templates_db.count()
        project_files_count = project_files_db.count()

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "database": {
                "status": "connected",
                "projects_count": projects_count,
                "templates_count": templates_count,
                "project_files_count": project_files_count,
            },
            "services": {
                "gemini_api": "configured" if settings.GEMINI_API_KEY else "not_configured",
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


# Projects endpoints
@api_router.get("/projects", tags=["Projects"])
async def get_projects():
    """Get all projects."""
    try:
        projects_db = get_projects_db()
        projects = projects_db.get_all()
        return {
            "projects": projects,
            "count": len(projects),
            "timestamp": time.time(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get projects: {str(e)}"
        )


@api_router.post("/projects", tags=["Projects"])
async def create_project(project_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Create a new project and trigger automatic analysis."""
    try:
        projects_db = get_projects_db()

        # Basic validation
        if not project_data.get("name"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project name is required"
            )

        # Generate ID if not provided
        if not project_data.get("id"):
            project_data["id"] = f"proj_{int(time.time())}_{hash(project_data['name']) % 10000:04d}"

        # Add timestamps
        current_time = time.time()
        iso_time = datetime.fromtimestamp(current_time).isoformat() + "Z"
        project_data.setdefault("created_at", iso_time)
        project_data.setdefault("updated_at", iso_time)

        # Add default fields
        project_data.setdefault("status", "draft")
        project_data.setdefault("description", "")
        project_data.setdefault("requirements", "")
        project_data.setdefault("tags", [])
        project_data.setdefault("metadata", {})
        project_data.setdefault("tech_stack", [])
        project_data.setdefault("file_structure", {})
        project_data.setdefault("tasks", [])
        project_data.setdefault("session_data", {})

        # Insert into database
        logger.info(f"About to insert project into database: {project_data['id']}")
        doc_id = projects_db.insert(project_data)
        logger.info(f"Project inserted with doc_id: {doc_id}")

        # Retrieve the created project using the project ID
        created_project = projects_db.get_by_id(project_data["id"])
        logger.info(f"Retrieved project after insertion: {created_project is not None}")
        if not created_project:
            # Fallback: use the original data
            logger.warning(f"Could not retrieve project {project_data['id']} after insertion, using original data")
            created_project = project_data

        return {
            "message": "Project created successfully.",
            "project": created_project,
            "doc_id": doc_id,
            "timestamp": current_time
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@api_router.get("/projects/{project_id}", tags=["Projects"])
async def get_project(project_id: str):
    """Get a specific project by ID."""
    try:
        projects_db = get_projects_db()
        project = projects_db.get_by_id(project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )

        return {
            "project": project,
            "timestamp": time.time(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )


@api_router.delete("/projects/{project_id}", tags=["Projects"])
async def delete_project(project_id: str):
    """Delete a project and all its related data."""
    try:
        projects_db = get_projects_db()

        # Check if project exists
        project = projects_db.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )

        # Delete the project itself
        project_deleted = projects_db.delete(project_id)

        if not project_deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project"
            )

        logger.info(f"Deleted project {project_id}")

        return {
            "message": "Project deleted successfully",
            "project_id": project_id,
            "timestamp": time.time(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )






# Templates endpoints
@api_router.get("/templates", tags=["Templates"])
async def get_templates():
    """Get all templates."""
    try:
        templates_db = get_templates_db()
        templates = templates_db.get_all()
        return {
            "templates": templates,
            "count": len(templates),
            "timestamp": time.time(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}"
        )



