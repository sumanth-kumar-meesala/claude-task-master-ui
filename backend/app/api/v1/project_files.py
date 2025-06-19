"""
Project Files API endpoints for managing generated project files.
"""

import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Query
from tinydb import Query as TinyQuery

from app.database.tinydb_handler import get_project_files_db, get_projects_db
from app.models.schemas import (
    ProjectFile, ProjectFileCreate, ProjectFileUpdate,
    ProjectFileType, ProjectFileStatus
)
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/project-files", tags=["Project Files"])


@router.get("/", response_model=List[ProjectFile])
async def get_project_files(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    file_type: Optional[ProjectFileType] = Query(None, description="Filter by file type"),
    status: Optional[ProjectFileStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of files to return")
):
    """Get project files with optional filtering."""
    try:
        project_files_db = get_project_files_db()
        
        # Build query
        query_conditions = []
        if project_id:
            query_conditions.append(TinyQuery().project_id == project_id)
        if file_type:
            query_conditions.append(TinyQuery().file_type == file_type.value)
        if status:
            query_conditions.append(TinyQuery().status == status.value)
        
        if query_conditions:
            # Combine conditions with AND
            combined_query = query_conditions[0]
            for condition in query_conditions[1:]:
                combined_query = combined_query & condition
            files = project_files_db.search(combined_query)
        else:
            files = project_files_db.get_all()
        
        # Apply limit
        files = files[:limit]
        
        return files
        
    except Exception as e:
        logger.error(f"Failed to get project files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project files: {str(e)}"
        )


@router.get("/{file_id}", response_model=ProjectFile)
async def get_project_file(file_id: str):
    """Get a specific project file by ID."""
    try:
        project_files_db = get_project_files_db()
        file_data = project_files_db.get_by_id(file_id)
        
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project file with ID {file_id} not found"
            )
        
        return file_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project file: {str(e)}"
        )


@router.post("/", response_model=ProjectFile)
async def create_project_file(file_data: ProjectFileCreate):
    """Create a new project file."""
    try:
        project_files_db = get_project_files_db()
        projects_db = get_projects_db()
        
        # Verify project exists
        project = projects_db.get_by_id(file_data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {file_data.project_id} not found"
            )
        
        # Generate file ID
        file_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # Prepare file data
        file_dict = file_data.model_dump()
        file_dict.update({
            "id": file_id,
            "created_at": now,
            "updated_at": now
        })
        
        # Set file size in metadata
        if file_dict["metadata"] is None:
            file_dict["metadata"] = {}
        file_dict["metadata"]["file_size"] = len(file_data.content)
        
        # Insert into database
        project_files_db.insert(file_dict)
        
        # Retrieve the created file
        created_file = project_files_db.get_by_id(file_id)
        if not created_file:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created file"
            )
        
        logger.info(f"Created project file {file_id} for project {file_data.project_id}")
        return created_file
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create project file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project file: {str(e)}"
        )


@router.put("/{file_id}", response_model=ProjectFile)
async def update_project_file(file_id: str, file_update: ProjectFileUpdate):
    """Update a project file."""
    try:
        project_files_db = get_project_files_db()
        
        # Check if file exists
        existing_file = project_files_db.get_by_id(file_id)
        if not existing_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project file with ID {file_id} not found"
            )
        
        # Prepare update data
        update_data = {}
        if file_update.file_name is not None:
            update_data["file_name"] = file_update.file_name
        if file_update.content is not None:
            update_data["content"] = file_update.content
            # Update file size in metadata
            if "metadata" not in update_data:
                update_data["metadata"] = existing_file.get("metadata", {})
            update_data["metadata"]["file_size"] = len(file_update.content)
        if file_update.metadata is not None:
            update_data["metadata"] = file_update.metadata.dict()
        if file_update.status is not None:
            update_data["status"] = file_update.status.value
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update in database
        project_files_db.update(update_data, TinyQuery().id == file_id)
        
        # Retrieve updated file
        updated_file = project_files_db.get_by_id(file_id)
        if not updated_file:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated file"
            )
        
        logger.info(f"Updated project file {file_id}")
        return updated_file
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project file: {str(e)}"
        )


@router.delete("/{file_id}")
async def delete_project_file(file_id: str):
    """Delete a project file."""
    try:
        project_files_db = get_project_files_db()
        
        # Check if file exists
        existing_file = project_files_db.get_by_id(file_id)
        if not existing_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project file with ID {file_id} not found"
            )
        
        # Delete from database
        deleted_count = project_files_db.delete(TinyQuery().id == file_id)
        
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project file"
            )
        
        logger.info(f"Deleted project file {file_id}")
        return {"message": "Project file deleted successfully", "file_id": file_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project file: {str(e)}"
        )


@router.get("/project/{project_id}/overview", response_model=Optional[ProjectFile])
async def get_project_overview(project_id: str):
    """Get the primary project overview file for a project."""
    try:
        project_files_db = get_project_files_db()
        
        # Look for primary project overview file
        files = project_files_db.search(
            (TinyQuery().project_id == project_id) &
            (TinyQuery().file_type == ProjectFileType.PROJECT_OVERVIEW.value) &
            (TinyQuery().metadata.is_primary == True)
        )
        
        if files:
            return files[0]
        
        # If no primary file, get the most recent project overview
        all_overviews = project_files_db.search(
            (TinyQuery().project_id == project_id) &
            (TinyQuery().file_type == ProjectFileType.PROJECT_OVERVIEW.value)
        )
        
        if all_overviews:
            # Sort by created_at descending and return the most recent
            sorted_overviews = sorted(all_overviews, key=lambda x: x.get("created_at", ""), reverse=True)
            return sorted_overviews[0]
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get project overview for {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project overview: {str(e)}"
        )


@router.get("/project/{project_id}/tasks", response_model=List[ProjectFile])
async def get_project_tasks(project_id: str):
    """Get all task files for a project."""
    try:
        project_files_db = get_project_files_db()
        
        # Get all task files and tasks index for the project
        task_files = project_files_db.search(
            (TinyQuery().project_id == project_id) &
            ((TinyQuery().file_type == ProjectFileType.TASK_FILE.value) |
             (TinyQuery().file_type == ProjectFileType.TASKS_INDEX.value))
        )
        
        # Sort by task number (for task files) and file type
        def sort_key(file_data):
            file_type = file_data.get("file_type", "")
            if file_type == ProjectFileType.TASKS_INDEX.value:
                return (0, 0)  # Index file comes first
            elif file_type == ProjectFileType.TASK_FILE.value:
                task_number = file_data.get("metadata", {}).get("task_number", 999)
                return (1, task_number)
            else:
                return (2, 0)
        
        sorted_files = sorted(task_files, key=sort_key)
        return sorted_files
        
    except Exception as e:
        logger.error(f"Failed to get project tasks for {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project tasks: {str(e)}"
        )
