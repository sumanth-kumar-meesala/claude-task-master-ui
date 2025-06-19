"""
Task Generation API endpoints using claude-task-master integration.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
import json
import asyncio
from datetime import datetime
import os

from app.services.task_master_service import task_master_service
from app.services.task_integration_service import task_integration_service
from app.services.prd_generation_service import prd_generation_service
from app.database.tinydb_handler import get_projects_db
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/task-generation", tags=["Task Generation"])


class PRDParseRequest(BaseModel):
    """Request model for PRD parsing."""
    project_id: str = Field(..., description="Project ID")
    prd_content: str = Field(..., description="PRD content to parse")
    num_tasks: int = Field(default=10, ge=1, le=50, description="Number of tasks to generate")
    research: bool = Field(default=False, description="Use research-backed generation")
    force: bool = Field(default=False, description="Force overwrite existing tasks")
    append: bool = Field(default=False, description="Append to existing tasks")


class TaskGenerationResponse(BaseModel):
    """Response model for task generation."""
    success: bool
    message: str
    project_id: Optional[str] = None
    tasks_count: Optional[int] = None
    tasks: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ProjectInitRequest(BaseModel):
    """Request model for project initialization."""
    project_id: str = Field(..., description="Project ID")
    project_name: Optional[str] = Field(None, description="Project name")


@router.post("/initialize-project", response_model=TaskGenerationResponse)
async def initialize_project(request: ProjectInitRequest):
    """Initialize a task-master project for the given project ID."""
    try:
        # Get project from database
        projects_db = get_projects_db()
        project = projects_db.get_by_id(request.project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Create project directory path
        project_path = os.path.join(settings.TINYDB_PATH, "generated_projects", request.project_id)
        
        # Initialize task-master project
        result = await task_master_service.initialize_project(
            project_path=project_path,
            project_name=request.project_name or project.get("name", "Untitled Project")
        )
        
        if result["success"]:
            # Update project with task-master info
            project["task_master_initialized"] = True
            project["task_master_path"] = project_path
            project["updated_at"] = datetime.now().isoformat()
            projects_db.update(project["id"], project)
            
            return TaskGenerationResponse(
                success=True,
                message="Project initialized successfully",
                project_id=request.project_id
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to initialize project: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/parse-prd", response_model=TaskGenerationResponse)
async def parse_prd(request: PRDParseRequest):
    """Parse a PRD and generate tasks using claude-task-master."""
    try:
        # Get project from database
        projects_db = get_projects_db()
        project = projects_db.get_by_id(request.project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get or create project path
        project_path = project.get("task_master_path")
        if not project_path:
            project_path = os.path.join(settings.TINYDB_PATH, "generated_projects", request.project_id)
            
            # Initialize if not already done
            init_result = await task_master_service.initialize_project(
                project_path=project_path,
                project_name=project.get("name", "Untitled Project")
            )
            
            if not init_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize project: {init_result.get('error', 'Unknown error')}"
                )
            
            # Update project with path
            project["task_master_path"] = project_path
            project["task_master_initialized"] = True
            projects_db.update(project["id"], project)
        
        # Parse PRD and generate tasks
        result = await task_master_service.parse_prd(
            prd_content=request.prd_content,
            project_path=project_path,
            num_tasks=request.num_tasks,
            research=request.research,
            force=request.force,
            append=request.append
        )
        
        if result["success"]:
            # Sync tasks to project files database
            sync_result = task_integration_service.sync_tasks_to_project_files(
                request.project_id,
                result.get("tasks", {})
            )

            # Update project with task generation info
            project["tasks_generated"] = True
            project["tasks_count"] = len(result.get("tasks", {}).get("master", {}).get("tasks", []))
            project["last_task_generation"] = datetime.now().isoformat()
            project["updated_at"] = datetime.now().isoformat()

            # Update task master config
            if "task_master_config" not in project:
                project["task_master_config"] = {}

            project["task_master_config"].update({
                "last_prd_content": request.prd_content,
                "use_research": request.research,
                "default_num_tasks": request.num_tasks
            })

            # Add to generation history
            if "generation_history" not in project["task_master_config"]:
                project["task_master_config"]["generation_history"] = []

            project["task_master_config"]["generation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "num_tasks": project["tasks_count"],
                "research_used": request.research,
                "success": True
            })

            projects_db.update(project["id"], project)

            return TaskGenerationResponse(
                success=True,
                message=f"{result['message']}. Synced {sync_result.get('synced_count', 0)} files to project database.",
                project_id=request.project_id,
                tasks_count=project["tasks_count"],
                tasks=result.get("tasks")
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse PRD: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing PRD: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/tasks/{project_id}", response_model=TaskGenerationResponse)
async def get_project_tasks(project_id: str):
    """Get all tasks for a project."""
    try:
        # Get project from database
        projects_db = get_projects_db()
        project = projects_db.get_by_id(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_path = project.get("task_master_path")
        if not project_path:
            raise HTTPException(status_code=404, detail="Project not initialized with task-master")
        
        # Get tasks
        result = await task_master_service.list_tasks(project_path)
        
        if result["success"]:
            return TaskGenerationResponse(
                success=True,
                message="Tasks retrieved successfully",
                project_id=project_id,
                tasks=result.get("tasks"),
                tasks_count=len(result.get("tasks", {}).get("master", {}).get("tasks", []))
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get tasks: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/next-task/{project_id}")
async def get_next_task(project_id: str):
    """Get the next task to work on for a project."""
    try:
        # Get project from database
        projects_db = get_projects_db()
        project = projects_db.get_by_id(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_path = project.get("task_master_path")
        if not project_path:
            raise HTTPException(status_code=404, detail="Project not initialized with task-master")
        
        # Get next task
        result = await task_master_service.get_next_task(project_path)
        
        if result["success"]:
            return {
                "success": True,
                "message": "Next task retrieved successfully",
                "project_id": project_id,
                "output": result["output"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get next task: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/project-status/{project_id}")
async def get_project_status(project_id: str):
    """Get the task-master status for a project."""
    try:
        # Get project from database
        projects_db = get_projects_db()
        project = projects_db.get_by_id(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "success": True,
            "project_id": project_id,
            "task_master_initialized": project.get("task_master_initialized", False),
            "tasks_generated": project.get("tasks_generated", False),
            "tasks_count": project.get("tasks_count", 0),
            "last_task_generation": project.get("last_task_generation"),
            "task_master_path": project.get("task_master_path")
        }
        
    except Exception as e:
        logger.error(f"Error getting project status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Streaming endpoint for real-time task generation feedback
@router.post("/parse-prd-stream/{project_id}")
async def parse_prd_stream(project_id: str, request: PRDParseRequest):
    """Stream task generation progress in real-time."""
    async def generate_stream():
        try:
            yield f"data: {json.dumps({'status': 'starting', 'message': 'Initializing task generation...'})}\n\n"
            
            # Get project from database
            projects_db = get_projects_db()
            project = projects_db.get_by_id(project_id)
            
            if not project:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Project not found'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Setting up project environment...'})}\n\n"
            
            # Get or create project path
            project_path = project.get("task_master_path")
            if not project_path:
                project_path = os.path.join(settings.TINYDB_PATH, "generated_projects", project_id)
                
                yield f"data: {json.dumps({'status': 'progress', 'message': 'Initializing task-master project...'})}\n\n"
                
                init_result = await task_master_service.initialize_project(
                    project_path=project_path,
                    project_name=project.get("name", "Untitled Project")
                )
                
                if not init_result["success"]:
                    error_msg = f"Failed to initialize: {init_result.get('error', 'Unknown error')}"
                    yield f"data: {json.dumps({'status': 'error', 'message': error_msg})}\n\n"
                    return
                
                project["task_master_path"] = project_path
                project["task_master_initialized"] = True
                logger.info(f"About to update project {project['id']} with task_master_path")
                projects_db.update(project["id"], project)
                logger.info(f"Successfully updated project {project['id']} with task_master_path")
            
            yield f"data: {json.dumps({'status': 'progress', 'message': 'Parsing PRD and generating tasks...'})}\n\n"
            
            # Parse PRD and generate tasks
            result = await task_master_service.parse_prd(
                prd_content=request.prd_content,
                project_path=project_path,
                num_tasks=request.num_tasks,
                research=request.research,
                force=request.force,
                append=request.append
            )
            
            if result["success"]:
                yield f"data: {json.dumps({'status': 'progress', 'message': 'Syncing tasks to project database...'})}\n\n"

                # Sync tasks to project files database
                sync_result = task_integration_service.sync_tasks_to_project_files(
                    project_id,
                    result.get("tasks", {})
                )

                # Update project
                project["tasks_generated"] = True
                project["tasks_count"] = len(result.get("tasks", {}).get("master", {}).get("tasks", []))
                project["last_task_generation"] = datetime.now().isoformat()
                project["updated_at"] = datetime.now().isoformat()

                # Update task master config
                if "task_master_config" not in project:
                    project["task_master_config"] = {}

                project["task_master_config"].update({
                    "last_prd_content": request.prd_content,
                    "use_research": request.research,
                    "default_num_tasks": request.num_tasks
                })

                # Add to generation history
                if "generation_history" not in project["task_master_config"]:
                    project["task_master_config"]["generation_history"] = []

                project["task_master_config"]["generation_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "num_tasks": project["tasks_count"],
                    "research_used": request.research,
                    "success": True
                })

                logger.info(f"About to update project {project['id']} with task generation results")
                projects_db.update(project["id"], project)
                logger.info(f"Successfully updated project {project['id']} with task generation results")

                final_message = f"{result['message']}. Synced {sync_result.get('synced_count', 0)} files to project database."
                yield f"data: {json.dumps({'status': 'complete', 'message': final_message, 'tasks': result.get('tasks'), 'tasks_count': project['tasks_count'], 'synced_files': sync_result.get('synced_count', 0)})}\n\n"
            else:
                error_msg = f"Failed to parse PRD: {result.get('error', 'Unknown error')}"
                yield f"data: {json.dumps({'status': 'error', 'message': error_msg})}\n\n"
                
        except Exception as e:
            logger.error(f"Error in streaming task generation: {str(e)}")
            yield f"data: {json.dumps({'status': 'error', 'message': f'Internal server error: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@router.get("/task-files/{project_id}")
async def get_project_task_files(project_id: str):
    """Get all task-related files for a project."""
    try:
        # Get project from database
        projects_db = get_projects_db()
        project = projects_db.get_by_id(project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get task files
        task_files = task_integration_service.get_project_task_files(project_id)

        return {
            "success": True,
            "project_id": project_id,
            "task_files": task_files,
            "files_count": len(task_files),
            "message": f"Retrieved {len(task_files)} task files"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/task-markdown-files/{project_id}")
async def get_task_markdown_files(project_id: str):
    """Get all generated markdown files for tasks."""
    try:
        # Get project from database
        projects_db = get_projects_db()
        project = projects_db.get_by_id(project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_path = project.get("task_master_path")
        if not project_path:
            raise HTTPException(status_code=404, detail="Project not initialized with task-master")

        # Get markdown files
        result = await task_master_service.get_task_markdown_files(project_path)

        if result["success"]:
            return {
                "success": True,
                "project_id": project_id,
                "markdown_files": result["files"],
                "files_count": result["count"],
                "message": f"Retrieved {result['count']} markdown files"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get markdown files: {result.get('error', 'Unknown error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task markdown files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/generate-prd/{project_id}")
async def generate_prd_content(project_id: str):
    """Generate PRD content from existing project data."""
    try:
        # Get project from database
        projects_db = get_projects_db()
        project = projects_db.get_by_id(project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Generate PRD content
        result = prd_generation_service.generate_prd_from_project(project_id)

        if result["success"]:
            # Also get suggestions for improvement
            suggestions_result = prd_generation_service.get_prd_suggestions(project_id)

            return {
                "success": True,
                "project_id": project_id,
                "prd_content": result["prd_content"],
                "project_name": result["project_name"],
                "has_existing_overview": result["has_existing_overview"],
                "generated_at": result["generated_at"],
                "suggestions": suggestions_result.get("suggestions", []),
                "completeness_score": suggestions_result.get("completeness_score", 0),
                "message": "PRD content generated successfully from project data"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate PRD: {result.get('error', 'Unknown error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PRD content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
