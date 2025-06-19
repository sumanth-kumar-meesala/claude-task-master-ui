"""
Task Integration Service

This service manages the integration between task-master generated tasks
and the existing project database schema and file management system.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from app.database.tinydb_handler import get_projects_db, get_project_files_db
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TaskIntegrationService:
    """Service for integrating task-master tasks with project management."""
    
    def __init__(self):
        self.projects_db = get_projects_db()
        self.project_files_db = get_project_files_db()
    
    def sync_tasks_to_project_files(self, project_id: str, tasks_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync task-master generated tasks to the project files database.
        
        Args:
            project_id: Project ID
            tasks_data: Task data from task-master (tasks.json content)
            
        Returns:
            Dictionary with sync results
        """
        try:
            # Extract tasks from the master tag
            master_tasks = tasks_data.get("master", {}).get("tasks", [])
            if not master_tasks:
                return {
                    "success": False,
                    "error": "No tasks found in master tag",
                    "synced_count": 0
                }
            
            synced_count = 0
            failed_count = 0
            
            # Create or update project overview file
            overview_result = self._create_project_overview_file(project_id, tasks_data)
            if overview_result["success"]:
                synced_count += 1
            else:
                failed_count += 1
            
            # Create individual task files
            for task in master_tasks:
                task_result = self._create_task_file(project_id, task)
                if task_result["success"]:
                    synced_count += 1
                else:
                    failed_count += 1
                    logger.error(f"Failed to sync task {task.get('id', 'unknown')}: {task_result.get('error')}")
            
            # Create tasks index file
            index_result = self._create_tasks_index_file(project_id, master_tasks)
            if index_result["success"]:
                synced_count += 1
            else:
                failed_count += 1
            
            return {
                "success": True,
                "synced_count": synced_count,
                "failed_count": failed_count,
                "total_tasks": len(master_tasks),
                "message": f"Synced {synced_count} files, {failed_count} failed"
            }
            
        except Exception as e:
            logger.error(f"Error syncing tasks to project files: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "synced_count": 0
            }
    
    def _create_project_overview_file(self, project_id: str, tasks_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a project overview file from task data."""
        try:
            master_data = tasks_data.get("master", {})
            tasks = master_data.get("tasks", [])
            metadata = master_data.get("metadata", {})
            
            # Generate overview content
            overview_content = self._generate_overview_content(tasks, metadata)
            
            # Create file record
            file_id = f"overview_{project_id}_{int(datetime.now().timestamp())}"
            file_record = {
                "id": file_id,
                "project_id": project_id,
                "file_type": "project_overview",
                "file_name": "ProjectOverview.md",
                "content": overview_content,
                "metadata": {
                    "generated_from": "task_master",
                    "tasks_count": len(tasks),
                    "generation_timestamp": datetime.now().isoformat(),
                    "is_primary": True
                },
                "status": "generated",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insert into database
            doc_id = self.project_files_db.insert(file_record)
            
            return {
                "success": True,
                "file_id": file_id,
                "doc_id": doc_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_task_file(self, project_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create an individual task file."""
        try:
            task_id = task.get("id", "unknown")
            task_title = task.get("title", "Untitled Task")
            
            # Generate task content
            task_content = self._generate_task_content(task)
            
            # Create file record
            file_id = f"task_{project_id}_{task_id}_{int(datetime.now().timestamp())}"
            file_record = {
                "id": file_id,
                "project_id": project_id,
                "file_type": "task_file",
                "file_name": f"Task_{task_id:03d}_{task_title.replace(' ', '_')}.md",
                "content": task_content,
                "metadata": {
                    "generated_from": "task_master",
                    "task_id": task_id,
                    "task_title": task_title,
                    "task_priority": task.get("priority", "medium"),
                    "task_status": task.get("status", "pending"),
                    "dependencies": task.get("dependencies", []),
                    "generation_timestamp": datetime.now().isoformat(),
                    "is_primary": False
                },
                "status": "generated",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insert into database
            doc_id = self.project_files_db.insert(file_record)
            
            return {
                "success": True,
                "file_id": file_id,
                "doc_id": doc_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_tasks_index_file(self, project_id: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a tasks index file."""
        try:
            # Generate index content
            index_content = self._generate_tasks_index_content(tasks)
            
            # Create file record
            file_id = f"tasks_index_{project_id}_{int(datetime.now().timestamp())}"
            file_record = {
                "id": file_id,
                "project_id": project_id,
                "file_type": "tasks_index",
                "file_name": "Tasks_Index.md",
                "content": index_content,
                "metadata": {
                    "generated_from": "task_master",
                    "tasks_count": len(tasks),
                    "generation_timestamp": datetime.now().isoformat(),
                    "is_primary": True
                },
                "status": "generated",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insert into database
            doc_id = self.project_files_db.insert(file_record)
            
            return {
                "success": True,
                "file_id": file_id,
                "doc_id": doc_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_overview_content(self, tasks: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
        """Generate project overview content from tasks with checklist format."""
        content = f"""# Project Overview

Generated from Task Master on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

This project consists of {len(tasks)} main tasks generated from the Product Requirements Document (PRD).

## Project Setup Checklist

- [ ] Review all project requirements and constraints
- [ ] Set up development environment
- [ ] Initialize project repository
- [ ] Configure development tools and dependencies
- [ ] Set up testing framework
- [ ] Configure CI/CD pipeline (if applicable)
- [ ] Set up documentation structure

## Task Breakdown Checklist

"""

        # Group tasks by priority
        high_priority = [t for t in tasks if t.get("priority") == "high"]
        medium_priority = [t for t in tasks if t.get("priority") == "medium"]
        low_priority = [t for t in tasks if t.get("priority") == "low"]

        if high_priority:
            content += "### High Priority Tasks\n"
            for task in high_priority:
                status = task.get("status", "pending")
                checkbox = "[x]" if status == "done" else "[ ]"
                content += f"- {checkbox} **Task {task.get('id')}**: {task.get('title')}\n"
            content += "\n"

        if medium_priority:
            content += "### Medium Priority Tasks\n"
            for task in medium_priority:
                status = task.get("status", "pending")
                checkbox = "[x]" if status == "done" else "[ ]"
                content += f"- {checkbox} **Task {task.get('id')}**: {task.get('title')}\n"
            content += "\n"

        if low_priority:
            content += "### Low Priority Tasks\n"
            for task in low_priority:
                status = task.get("status", "pending")
                checkbox = "[x]" if status == "done" else "[ ]"
                content += f"- {checkbox} **Task {task.get('id')}**: {task.get('title')}\n"
            content += "\n"

        content += """## Project Milestones Checklist

- [ ] Phase 1: High priority tasks completed
- [ ] Phase 2: Medium priority tasks completed
- [ ] Phase 3: Low priority tasks completed
- [ ] Integration testing completed
- [ ] Performance testing completed
- [ ] Security review completed
- [ ] Documentation finalized
- [ ] Code review completed
- [ ] Deployment preparation completed
- [ ] Project ready for release

## Quality Assurance Checklist

- [ ] All code follows project standards
- [ ] All tests are passing
- [ ] Code coverage meets requirements
- [ ] No security vulnerabilities
- [ ] Performance requirements met
- [ ] Documentation is complete and accurate
- [ ] All dependencies are up to date
- [ ] Error handling is comprehensive

## Implementation Notes

Each task has been designed to be atomic and focused on a single responsibility. Tasks are ordered logically considering dependencies and implementation sequence.

For detailed information about each task, refer to the individual task files.
"""

        return content
    
    def _generate_task_content(self, task: Dict[str, Any]) -> str:
        """Generate markdown content for a single task with comprehensive checklists."""
        task_id = task.get("id", "unknown")
        title = task.get("title", "Untitled Task")
        description = task.get("description", "No description provided")
        details = task.get("details", "")
        test_strategy = task.get("testStrategy", "")
        priority = task.get("priority", "medium")
        status = task.get("status", "pending")
        dependencies = task.get("dependencies", [])

        content = f"""# Task {task_id}: {title}

## Overview

**Priority**: {priority.title()}
**Status**: {status.title()}
**Dependencies**: {', '.join([f'Task {dep}' for dep in dependencies]) if dependencies else 'None'}

## Description

{description}

## Dependencies Checklist
"""

        if dependencies:
            for dep in dependencies:
                content += f"- [ ] Ensure Task {dep} is completed\n"
            content += "- [ ] Verify all dependencies are satisfied before starting\n"
        else:
            content += "- [ ] Confirm no dependencies are required\n"
            content += "- [ ] Verify task can be started independently\n"

        content += "\n"

        if details:
            content += f"""## Implementation Details Checklist

"""
            # Convert implementation details into actionable checklist items
            detail_lines = [line.strip() for line in details.split('\n') if line.strip()]
            for line in detail_lines:
                if line and not line.startswith('-'):
                    content += f"- [ ] {line}\n"
                elif line.startswith('-'):
                    # Already a list item, convert to checklist
                    content += f"- [ ] {line[1:].strip()}\n"

            content += "\n"
        else:
            content += """## Implementation Checklist

- [ ] Research technical requirements and constraints
- [ ] Design technical solution approach
- [ ] Identify potential technical challenges
- [ ] Plan implementation strategy
- [ ] Set up development environment for this task
- [ ] Create feature branch for this task

"""

        if test_strategy:
            content += f"""## Testing Checklist

"""
            # Convert test strategy into actionable checklist items
            test_lines = [line.strip() for line in test_strategy.split('\n') if line.strip()]
            for line in test_lines:
                if line and not line.startswith('-'):
                    content += f"- [ ] {line}\n"
                elif line.startswith('-'):
                    # Already a list item, convert to checklist
                    content += f"- [ ] {line[1:].strip()}\n"

            content += "\n"
        else:
            content += """## Testing Checklist

- [ ] Write unit tests for new functionality
- [ ] Write integration tests if applicable
- [ ] Test edge cases and error conditions
- [ ] Verify performance requirements are met
- [ ] Run all existing tests to ensure no regressions

"""

        content += f"""## Acceptance Criteria Checklist

- [ ] Task implementation is complete
- [ ] All functionality works as described
- [ ] Code follows project standards and conventions
- [ ] Code is properly documented with comments
- [ ] All tests are written and passing
- [ ] No security vulnerabilities introduced
- [ ] Performance impact is acceptable
- [ ] Error handling is comprehensive
- [ ] Documentation is updated (if applicable)
- [ ] Code review is completed and approved

## Implementation Workflow Checklist

- [ ] Review task requirements and dependencies
- [ ] Set up development environment for this task
- [ ] Create feature branch for this task
- [ ] Implement core functionality
- [ ] Write and run unit tests
- [ ] Update documentation
- [ ] Code review and refactoring
- [ ] Integration testing
- [ ] Merge to main branch
- [ ] Mark task as complete

## Quality Assurance Checklist

- [ ] Code follows project coding standards
- [ ] All tests pass successfully
- [ ] No security vulnerabilities introduced
- [ ] Performance impact is acceptable
- [ ] Error handling is comprehensive
- [ ] Code is properly documented
- [ ] Changes are backward compatible (if required)
- [ ] No breaking changes without proper versioning

---

*Generated by Task Master on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return content
    
    def _generate_tasks_index_content(self, tasks: List[Dict[str, Any]]) -> str:
        """Generate tasks index content with checklist format."""
        content = f"""# Tasks Index

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Tasks: {len(tasks)}

## Task Progress Checklist

"""

        # Group tasks by priority for better organization
        high_priority = [t for t in tasks if t.get("priority") == "high"]
        medium_priority = [t for t in tasks if t.get("priority") == "medium"]
        low_priority = [t for t in tasks if t.get("priority") == "low"]

        if high_priority:
            content += "### High Priority Tasks\n"
            for task in sorted(high_priority, key=lambda x: x.get("id", 0)):
                task_id = task.get("id", "?")
                title = task.get("title", "Untitled")
                status = task.get("status", "pending")
                checkbox = "[x]" if status == "done" else "[ ]"
                content += f"- {checkbox} **Task {task_id}**: {title}\n"
            content += "\n"

        if medium_priority:
            content += "### Medium Priority Tasks\n"
            for task in sorted(medium_priority, key=lambda x: x.get("id", 0)):
                task_id = task.get("id", "?")
                title = task.get("title", "Untitled")
                status = task.get("status", "pending")
                checkbox = "[x]" if status == "done" else "[ ]"
                content += f"- {checkbox} **Task {task_id}**: {title}\n"
            content += "\n"

        if low_priority:
            content += "### Low Priority Tasks\n"
            for task in sorted(low_priority, key=lambda x: x.get("id", 0)):
                task_id = task.get("id", "?")
                title = task.get("title", "Untitled")
                status = task.get("status", "pending")
                checkbox = "[x]" if status == "done" else "[ ]"
                content += f"- {checkbox} **Task {task_id}**: {title}\n"
            content += "\n"

        content += """## Project Completion Checklist

- [ ] All high priority tasks completed
- [ ] All medium priority tasks completed
- [ ] All low priority tasks completed
- [ ] Integration testing completed
- [ ] Documentation finalized
- [ ] Code review completed
- [ ] Performance testing completed
- [ ] Security review completed
- [ ] Deployment preparation completed
- [ ] Project ready for release

## Task Details Table

| ID | Title | Priority | Status | Dependencies |
|----|-------|----------|--------|--------------|
"""

        for task in sorted(tasks, key=lambda x: x.get("id", 0)):
            task_id = task.get("id", "?")
            title = task.get("title", "Untitled")
            priority = task.get("priority", "medium")
            status = task.get("status", "pending")
            deps = task.get("dependencies", [])
            deps_str = ", ".join([f"#{dep}" for dep in deps]) if deps else "None"

            content += f"| {task_id} | {title} | {priority} | {status} | {deps_str} |\n"

        content += """
## Task Dependencies

The following shows the task dependencies:

```
"""

        # Simple dependency visualization
        for task in sorted(tasks, key=lambda x: x.get("id", 0)):
            task_id = task.get("id")
            deps = task.get("dependencies", [])
            if deps:
                content += f"Task {task_id} depends on: {', '.join([f'Task {dep}' for dep in deps])}\n"

        content += "```\n"

        return content
    
    def get_project_task_files(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all task-related files for a project."""
        try:
            # Get all files for the project that are task-related
            all_files = self.project_files_db.get_all()
            task_files = [
                file for file in all_files 
                if file.get("project_id") == project_id and 
                file.get("metadata", {}).get("generated_from") == "task_master"
            ]
            
            return task_files
            
        except Exception as e:
            logger.error(f"Error getting project task files: {str(e)}")
            return []


# Global instance
task_integration_service = TaskIntegrationService()
