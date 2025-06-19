"""
File Management API endpoints.

This module provides comprehensive file management for generated
ProjectOverview.md and task files.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import Response

from app.models.responses import SuccessResponse, ErrorResponse
from app.database.tinydb_handler import get_generated_files_db, get_task_definitions_db
from app.services.project_overview_generator import ProjectOverviewGenerator
from app.services.task_generator import TaskGenerator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/file-management", tags=["File Management"])

# Service instances
overview_generator = ProjectOverviewGenerator()
task_generator = TaskGenerator()


@router.get("/projects/{project_id}/files", response_model=SuccessResponse)
async def get_project_files(
    project_id: str,
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    include_content: bool = Query(False, description="Include file content in response")
):
    """
    Get all generated files for a project.
    
    Args:
        project_id: Project ID
        file_type: Optional file type filter
        include_content: Whether to include file content
        
    Returns:
        List of project files
    """
    try:
        logger.info(f"Getting files for project {project_id}")
        
        # Get files from database
        generated_files_db = get_generated_files_db()
        all_files = generated_files_db.get_all()
        
        # Filter by project
        project_files = [
            file for file in all_files
            if file.get("project_id") == project_id
        ]
        
        # Filter by file type if specified
        if file_type:
            project_files = [
                file for file in project_files
                if file.get("file_type") == file_type
            ]
        
        # Remove content if not requested
        if not include_content:
            for file in project_files:
                if "content" in file:
                    file["content_length"] = len(file["content"])
                    del file["content"]
        
        # Sort by creation date
        project_files.sort(key=lambda f: f.get("created_at", ""), reverse=True)
        
        return SuccessResponse(
            message="Project files retrieved successfully",
            data={
                "project_id": project_id,
                "files": project_files,
                "total_files": len(project_files),
                "file_types": list(set(f.get("file_type", "unknown") for f in project_files))
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project files"
        )


@router.get("/files/{file_id}", response_model=SuccessResponse)
async def get_file_by_id(file_id: str):
    """
    Get a specific file by ID.
    
    Args:
        file_id: File ID
        
    Returns:
        File data with content
    """
    try:
        generated_files_db = get_generated_files_db()
        file_data = generated_files_db.get_by_id(file_id)
        
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )
        
        return SuccessResponse(
            message="File retrieved successfully",
            data=file_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get file"
        )


@router.get("/files/{file_id}/download")
async def download_file(file_id: str):
    """
    Download a file as attachment.
    
    Args:
        file_id: File ID
        
    Returns:
        File content as download
    """
    try:
        generated_files_db = get_generated_files_db()
        file_data = generated_files_db.get_by_id(file_id)
        
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )
        
        content = file_data.get("content", "")
        filename = file_data.get("file_name", "file.md")
        
        return Response(
            content=content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download file"
        )


@router.get("/projects/{project_id}/overview", response_model=SuccessResponse)
async def get_project_overview(project_id: str):
    """
    Get project overview file.
    
    Args:
        project_id: Project ID
        
    Returns:
        Project overview file data
    """
    try:
        overview = await overview_generator.get_project_overview(project_id)
        
        if not overview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project overview not found for project {project_id}"
            )
        
        return SuccessResponse(
            message="Project overview retrieved successfully",
            data=overview
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project overview"
        )


@router.get("/projects/{project_id}/structure", response_model=SuccessResponse)
async def get_project_structure(project_id: str):
    """
    Get project structure.
    
    Args:
        project_id: Project ID
        
    Returns:
        Project structure data
    """
    try:
        structure = await overview_generator.get_project_structure(project_id)
        
        if not structure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project structure not found for project {project_id}"
            )
        
        return SuccessResponse(
            message="Project structure retrieved successfully",
            data=structure
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project structure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project structure"
        )


@router.get("/projects/{project_id}/tasks", response_model=SuccessResponse)
async def get_project_tasks(project_id: str):
    """
    Get all tasks for a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        List of project tasks
    """
    try:
        tasks = await task_generator.get_project_tasks(project_id)
        
        return SuccessResponse(
            message="Project tasks retrieved successfully",
            data={
                "project_id": project_id,
                "tasks": tasks,
                "total_tasks": len(tasks),
                "categories": list(set(task.get("category", "general") for task in tasks))
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting project tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project tasks"
        )


@router.get("/projects/{project_id}/task-files", response_model=SuccessResponse)
async def get_project_task_files(project_id: str):
    """
    Get all task files for a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        List of task files
    """
    try:
        task_files = await task_generator.get_task_files(project_id)
        
        return SuccessResponse(
            message="Project task files retrieved successfully",
            data={
                "project_id": project_id,
                "task_files": task_files,
                "total_files": len(task_files)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting project task files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project task files"
        )


@router.put("/files/{file_id}", response_model=SuccessResponse)
async def update_file_content(file_id: str, update_data: Dict[str, Any]):
    """
    Update file content.
    
    Args:
        file_id: File ID
        update_data: Update data including content
        
    Returns:
        Updated file data
    """
    try:
        generated_files_db = get_generated_files_db()
        file_data = generated_files_db.get_by_id(file_id)
        
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )
        
        # Update file data
        if "content" in update_data:
            file_data["content"] = update_data["content"]
        
        if "file_name" in update_data:
            file_data["file_name"] = update_data["file_name"]
        
        # Update metadata
        from datetime import datetime
        file_data["updated_at"] = datetime.utcnow().isoformat()
        file_data["version"] = file_data.get("version", 1) + 1
        
        # Save to database
        generated_files_db.update_by_id(file_id, file_data)
        
        return SuccessResponse(
            message="File updated successfully",
            data=file_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update file"
        )


@router.delete("/files/{file_id}", response_model=SuccessResponse)
async def delete_file(file_id: str):
    """
    Delete a file.
    
    Args:
        file_id: File ID
        
    Returns:
        Deletion confirmation
    """
    try:
        generated_files_db = get_generated_files_db()
        
        # Check if file exists
        file_data = generated_files_db.get_by_id(file_id)
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )
        
        # Delete file
        deleted = generated_files_db.delete_by_id(file_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file"
            )
        
        return SuccessResponse(
            message="File deleted successfully",
            data={
                "file_id": file_id,
                "file_name": file_data.get("file_name"),
                "deleted": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )


@router.post("/projects/{project_id}/export", response_model=SuccessResponse)
async def export_project_files(project_id: str, export_format: str = "zip"):
    """
    Export all project files in specified format.
    
    Args:
        project_id: Project ID
        export_format: Export format (zip, tar, etc.)
        
    Returns:
        Export information
    """
    try:
        # Get all project files
        generated_files_db = get_generated_files_db()
        all_files = generated_files_db.get_all()
        
        project_files = [
            file for file in all_files
            if file.get("project_id") == project_id
        ]
        
        if not project_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No files found for project {project_id}"
            )
        
        # For now, return file list (actual export implementation would create archive)
        export_data = {
            "project_id": project_id,
            "export_format": export_format,
            "files": [
                {
                    "file_name": file.get("file_name"),
                    "file_type": file.get("file_type"),
                    "size": len(file.get("content", "")),
                    "created_at": file.get("created_at")
                }
                for file in project_files
            ],
            "total_files": len(project_files),
            "total_size": sum(len(file.get("content", "")) for file in project_files)
        }
        
        return SuccessResponse(
            message="Project files export prepared",
            data=export_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting project files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export project files"
        )


# Health check for file management service
@router.get("/health", response_model=SuccessResponse)
async def file_management_health():
    """Health check for file management service."""
    try:
        # Test database connections
        generated_files_db = get_generated_files_db()
        task_definitions_db = get_task_definitions_db()
        
        # Simple database tests
        files_test = generated_files_db.get_all(limit=1)
        tasks_test = task_definitions_db.get_all(limit=1)
        
        return SuccessResponse(
            message="File management service is healthy",
            data={
                "service": "file_management",
                "status": "healthy",
                "databases": {
                    "generated_files": "connected",
                    "task_definitions": "connected"
                },
                "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"File management service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="File management service is unhealthy"
        )
