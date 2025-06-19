"""
File Storage Service for managing generated project files.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.database.tinydb_handler import get_project_files_db, get_projects_db
from app.models.schemas import ProjectFileType, ProjectFileStatus, ProjectFileMetadata
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class FileStorageService:
    """Service for managing project file storage and retrieval."""
    
    def __init__(self):
        self.project_files_db = get_project_files_db()
        self.projects_db = get_projects_db()
    
    async def save_project_overview(
        self,
        project_id: str,
        content: str,
        orchestration_id: Optional[str] = None,
        session_id: Optional[str] = None,
        agents_used: Optional[List[str]] = None,
        generation_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a project overview file.
        
        Args:
            project_id: ID of the associated project
            content: The overview content
            orchestration_id: Optional orchestration ID
            session_id: Optional session ID
            agents_used: List of agents that generated the content
            generation_context: Context used for generation
            
        Returns:
            The ID of the created file
        """
        try:
            # Verify project exists
            project = self.projects_db.get_by_id(project_id)
            if not project:
                raise ValidationException(f"Project {project_id} not found")
            
            # Mark any existing primary overview as non-primary
            await self._unmark_primary_overview(project_id)
            
            # Create metadata
            metadata = ProjectFileMetadata(
                agents_used=agents_used or [],
                generation_context=generation_context or {},
                file_size=len(content),
                is_primary=True
            )
            
            # Create file data
            file_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            file_data = {
                "id": file_id,
                "project_id": project_id,
                "orchestration_id": orchestration_id,
                "session_id": session_id,
                "file_type": ProjectFileType.PROJECT_OVERVIEW.value,
                "file_name": "ProjectOverview.md",
                "content": content,
                "metadata": metadata.model_dump(),
                "status": ProjectFileStatus.GENERATED.value,
                "created_at": now,
                "updated_at": now
            }
            
            # Save to database
            self.project_files_db.insert(file_data)
            
            logger.info(f"Saved project overview {file_id} for project {project_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to save project overview for {project_id}: {e}")
            raise
    
    async def save_task_files(
        self,
        project_id: str,
        task_files: List[Dict[str, Any]],
        orchestration_id: Optional[str] = None,
        session_id: Optional[str] = None,
        agents_used: Optional[List[str]] = None,
        generation_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Save multiple task files.
        
        Args:
            project_id: ID of the associated project
            task_files: List of task file data with 'name', 'content', and optional 'task_number'
            orchestration_id: Optional orchestration ID
            session_id: Optional session ID
            agents_used: List of agents that generated the content
            generation_context: Context used for generation
            
        Returns:
            List of created file IDs
        """
        try:
            # Verify project exists
            project = self.projects_db.get_by_id(project_id)
            if not project:
                raise ValidationException(f"Project {project_id} not found")
            
            file_ids = []
            now = datetime.utcnow().isoformat()
            
            for task_file in task_files:
                file_name = task_file.get("name", "Task.md")
                content = task_file.get("content", "")
                task_number = task_file.get("task_number")
                
                # Determine file type
                if "index" in file_name.lower() or "tasks_index" in file_name.lower():
                    file_type = ProjectFileType.TASKS_INDEX
                else:
                    file_type = ProjectFileType.TASK_FILE
                
                # Create metadata
                metadata = ProjectFileMetadata(
                    agents_used=agents_used or [],
                    generation_context=generation_context or {},
                    file_size=len(content),
                    task_number=task_number,
                    is_primary=False
                )
                
                # Create file data
                file_id = str(uuid.uuid4())
                
                file_data = {
                    "id": file_id,
                    "project_id": project_id,
                    "orchestration_id": orchestration_id,
                    "session_id": session_id,
                    "file_type": file_type.value,
                    "file_name": file_name,
                    "content": content,
                    "metadata": metadata.model_dump(),
                    "status": ProjectFileStatus.GENERATED.value,
                    "created_at": now,
                    "updated_at": now
                }
                
                # Save to database
                self.project_files_db.insert(file_data)
                file_ids.append(file_id)
                
                logger.info(f"Saved task file {file_id} ({file_name}) for project {project_id}")
            
            return file_ids
            
        except Exception as e:
            logger.error(f"Failed to save task files for {project_id}: {e}")
            raise
    
    async def save_orchestration_files(
        self,
        project_id: str,
        orchestration_result: Dict[str, Any],
        orchestration_id: str
    ) -> Dict[str, List[str]]:
        """
        Save all files generated from an orchestration result.
        
        Args:
            project_id: ID of the associated project
            orchestration_result: The orchestration result containing agent outputs
            orchestration_id: ID of the orchestration
            
        Returns:
            Dictionary with 'overview_files' and 'task_files' lists of file IDs
        """
        try:
            project_context = orchestration_result.get("project_context", {})
            agent_outputs = orchestration_result.get("agent_outputs", {})
            agents_used = orchestration_result.get("selected_agents", [])
            
            # Generate overview content
            overview_content = self._generate_overview_content(project_context, agent_outputs)
            
            # Save project overview
            overview_file_id = await self.save_project_overview(
                project_id=project_id,
                content=overview_content,
                orchestration_id=orchestration_id,
                agents_used=agents_used,
                generation_context=project_context
            )
            
            # Generate task files
            task_files_data = self._generate_task_files_data(project_context, agent_outputs)
            
            # Save task files
            task_file_ids = await self.save_task_files(
                project_id=project_id,
                task_files=task_files_data,
                orchestration_id=orchestration_id,
                agents_used=agents_used,
                generation_context=project_context
            )
            
            logger.info(f"Saved orchestration files for project {project_id}: "
                       f"1 overview, {len(task_file_ids)} task files")
            
            return {
                "overview_files": [overview_file_id],
                "task_files": task_file_ids
            }
            
        except Exception as e:
            logger.error(f"Failed to save orchestration files for {project_id}: {e}")
            raise
    
    async def get_project_files(
        self,
        project_id: str,
        file_type: Optional[ProjectFileType] = None
    ) -> List[Dict[str, Any]]:
        """Get all files for a project, optionally filtered by type."""
        try:
            from tinydb import Query
            
            query = Query().project_id == project_id
            if file_type:
                query = query & (Query().file_type == file_type.value)
            
            files = self.project_files_db.search(query)
            return files
            
        except Exception as e:
            logger.error(f"Failed to get project files for {project_id}: {e}")
            raise
    
    async def get_project_overview(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get the primary project overview for a project."""
        try:
            from tinydb import Query
            
            # Look for primary overview
            files = self.project_files_db.search(
                (Query().project_id == project_id) &
                (Query().file_type == ProjectFileType.PROJECT_OVERVIEW.value) &
                (Query().metadata.is_primary == True)
            )
            
            if files:
                return files[0]
            
            # If no primary, get most recent
            all_overviews = self.project_files_db.search(
                (Query().project_id == project_id) &
                (Query().file_type == ProjectFileType.PROJECT_OVERVIEW.value)
            )
            
            if all_overviews:
                sorted_overviews = sorted(all_overviews, key=lambda x: x.get("created_at", ""), reverse=True)
                return sorted_overviews[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get project overview for {project_id}: {e}")
            raise
    
    async def _unmark_primary_overview(self, project_id: str) -> None:
        """Unmark any existing primary overview for a project."""
        try:
            from tinydb import Query
            
            # Find existing primary overviews
            existing_primary = self.project_files_db.search(
                (Query().project_id == project_id) &
                (Query().file_type == ProjectFileType.PROJECT_OVERVIEW.value) &
                (Query().metadata.is_primary == True)
            )
            
            # Update them to non-primary
            for file_data in existing_primary:
                metadata = file_data.get("metadata", {})
                metadata["is_primary"] = False
                
                self.project_files_db.update(
                    {
                        "metadata": metadata,
                        "updated_at": datetime.utcnow().isoformat()
                    },
                    Query().id == file_data["id"]
                )
                
        except Exception as e:
            logger.error(f"Failed to unmark primary overview for {project_id}: {e}")
            # Don't raise here as this is a cleanup operation
    
    def _generate_overview_content(self, project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> str:
        """Generate project overview content from orchestration results."""
        # Import the existing function from chat.py
        from app.api.v1.chat import generate_project_overview_content
        return generate_project_overview_content(project_context, agent_outputs)
    
    def _generate_task_files_data(self, project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate task files data from orchestration results."""
        # Import the existing function from chat.py
        from app.api.v1.chat import generate_comprehensive_tasks, generate_tasks_index
        
        project_name = project_context.get("project_name", "Project")
        task_definitions = generate_comprehensive_tasks(project_context, agent_outputs)
        
        task_files = []
        
        # Generate individual task files
        for i, task_def in enumerate(task_definitions, 1):
            task_content = f"""# Task {i}: {task_def['title']}

## Description
{task_def['description']}

## Acceptance Criteria
{task_def.get('acceptance_criteria', 'To be defined')}

## Dependencies
{task_def.get('dependencies', 'None')}

## Estimated Effort
{task_def.get('estimated_effort', 'To be estimated')}

## Technical Notes
{task_def.get('technical_notes', 'None')}

---
*Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""
            
            task_files.append({
                "name": f"Task{i}.md",
                "content": task_content,
                "task_number": i
            })
        
        # Generate tasks index
        index_content = generate_tasks_index(project_name, task_definitions)
        task_files.append({
            "name": "TASKS_INDEX.md",
            "content": index_content
        })
        
        return task_files


# Global service instance
_file_storage_service: Optional[FileStorageService] = None


def get_file_storage_service() -> FileStorageService:
    """Get the global file storage service instance."""
    global _file_storage_service
    if _file_storage_service is None:
        _file_storage_service = FileStorageService()
    return _file_storage_service
