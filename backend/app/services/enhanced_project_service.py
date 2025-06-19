"""
Enhanced Project Service for the new workflow.

This service handles comprehensive project creation, data capture,
and preparation for agent orchestration.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.database.tinydb_handler import get_projects_db
from app.models.schemas import (
    ProjectCreate, Project
)
from app.core.exceptions import ValidationException, DatabaseException

logger = logging.getLogger(__name__)


class EnhancedProjectService:
    """Enhanced service for comprehensive project management."""
    
    def __init__(self):
        """Initialize the enhanced project service."""
        self.projects_db = get_projects_db()
        logger.info("Enhanced Project Service initialized")
    
    async def create_comprehensive_project(self, project_data: ProjectCreate) -> Dict[str, Any]:
        """
        Create a comprehensive project with all required details.
        
        This method captures all project information upfront before
        proceeding to agent orchestration.
        
        Args:
            project_data: Comprehensive project creation data
            
        Returns:
            Created project with validation status
            
        Raises:
            ValidationException: If project data is incomplete
            DatabaseException: If database operation fails
        """
        try:
            logger.info(f"Creating comprehensive project: {project_data.name}")
            
            # Validate comprehensive project data
            validation_result = await self._validate_comprehensive_project(project_data)
            if not validation_result["is_valid"]:
                raise ValidationException(
                    f"Project validation failed: {validation_result['errors']}"
                )
            
            # Generate project ID
            project_id = str(uuid.uuid4())
            
            # Prepare project data for database
            project_dict = project_data.model_dump()
            project_dict.update({
                "id": project_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "draft",
                "is_ready_for_orchestration": True  # Mark as ready since we have comprehensive data
            })
            
            # Save to database
            doc_id = self.projects_db.insert(project_dict)
            logger.info(f"Project {project_id} saved to database with doc_id: {doc_id}")
            
            # Retrieve the saved project
            saved_project = self.projects_db.get_by_id(project_id)
            if not saved_project:
                raise DatabaseException("Failed to retrieve saved project")
            
            return {
                "project": saved_project,
                "validation": validation_result,
                "ready_for_orchestration": True,
                "next_steps": [
                    "Select agents for collaboration",
                    "Start agent orchestration",
                    "Generate project overview and tasks"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to create comprehensive project: {e}")
            raise
    
    async def _validate_comprehensive_project(self, project_data: ProjectCreate) -> Dict[str, Any]:
        """
        Validate that project data is comprehensive enough for orchestration.
        
        Args:
            project_data: Project data to validate
            
        Returns:
            Validation result with details
        """
        errors = []
        warnings = []
        
        # Required fields validation
        required_fields = {
            "name": "Project name is required",
            "description": "Detailed project description is required",
            "requirements": "Project requirements are required"
        }
        
        for field, message in required_fields.items():
            value = getattr(project_data, field, None)
            if not value or (isinstance(value, str) and len(value.strip()) < 10):
                errors.append(message)
        
        # Recommended fields validation
        recommended_fields = {
            "tech_stack": "Technology stack guides technical decisions"
        }

        for field, message in recommended_fields.items():
            value = getattr(project_data, field, None)
            if not value or (isinstance(value, list) and len(value) == 0):
                warnings.append(message)
        
        # Tech stack validation
        if project_data.tech_stack and len(project_data.tech_stack) == 0:
            warnings.append("Technology stack should be specified for better agent guidance")
        
        # Agent selection validation
        if not project_data.selected_agents or len(project_data.selected_agents) == 0:
            errors.append("At least one agent must be selected for orchestration")
        elif len(project_data.selected_agents) < 2:
            warnings.append("Multiple agents are recommended for comprehensive analysis")
        
        # Description length validation
        if project_data.description and len(project_data.description) < 50:
            warnings.append("More detailed description will help agents provide better analysis")
        
        # Requirements validation
        if project_data.requirements and len(project_data.requirements) < 30:
            warnings.append("More detailed requirements will improve task generation quality")
        
        is_valid = len(errors) == 0
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "completeness_score": self._calculate_completeness_score(project_data),
            "recommendations": self._get_improvement_recommendations(project_data, warnings)
        }
    
    def _calculate_completeness_score(self, project_data: ProjectCreate) -> float:
        """Calculate project data completeness score (0-100)."""
        total_fields = 7  # Total number of important fields
        completed_fields = 0

        # Core fields (weight: 3)
        core_fields = ["name", "description", "requirements"]
        for field in core_fields:
            value = getattr(project_data, field, None)
            if value and len(str(value).strip()) >= 10:
                completed_fields += 3

        # Important fields (weight: 2)
        important_fields = ["tech_stack"]
        for field in important_fields:
            value = getattr(project_data, field, None)
            if value and (
                (isinstance(value, str) and len(value.strip()) > 0) or
                (isinstance(value, list) and len(value) > 0)
            ):
                completed_fields += 2

        # Optional fields (weight: 1)
        optional_fields = [
            "estimated_timeline", "team_size", "priority_level"
        ]
        for field in optional_fields:
            value = getattr(project_data, field, None)
            if value and len(str(value).strip()) > 0:
                completed_fields += 1

        max_score = (len(core_fields) * 3) + (len(important_fields) * 2) + len(optional_fields)
        return min(100, (completed_fields / max_score) * 100)
    
    def _get_improvement_recommendations(self, project_data: ProjectCreate, warnings: List[str]) -> List[str]:
        """Get specific recommendations for improving project data."""
        recommendations = []

        if not project_data.tech_stack or len(project_data.tech_stack) == 0:
            recommendations.append("Select preferred technologies to guide architecture decisions")
        
        if not project_data.scalability_requirements:
            recommendations.append("Define scalability requirements for proper system design")
        
        if len(project_data.selected_agents) < 3:
            recommendations.append("Consider adding more specialized agents for comprehensive analysis")
        
        return recommendations
    
    async def get_project_for_orchestration(self, project_id: str) -> Dict[str, Any]:
        """
        Retrieve complete project data for agent orchestration.
        
        Args:
            project_id: Project ID
            
        Returns:
            Complete project context for agents
        """
        try:
            project = self.projects_db.get_by_id(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            

            
            # Prepare comprehensive context for agents
            orchestration_context = {
                "project_id": project_id,
                "project_data": project,
                "comprehensive_requirements": self._build_comprehensive_requirements(project),
                "agent_instructions": self._build_agent_instructions(project),
                "collaboration_guidelines": self._get_collaboration_guidelines(),
                "expected_outputs": self._get_expected_outputs()
            }
            
            logger.info(f"Prepared orchestration context for project {project_id}")
            return orchestration_context
            
        except Exception as e:
            logger.error(f"Failed to get project for orchestration: {e}")
            raise
    
    def _build_comprehensive_requirements(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive requirements document for agents."""
        return {
            "core_requirements": {
                "name": project.get("name"),
                "description": project.get("description"),
                "requirements": project.get("requirements"),
                "objectives": project.get("objectives"),
                "success_criteria": project.get("success_criteria")
            },
            "technical_requirements": {
                "tech_stack": project.get("tech_stack", [])
            },
            "business_requirements": {
                "target_audience": project.get("target_audience"),
                "business_context": project.get("business_context"),
                "constraints": project.get("constraints"),
                "estimated_timeline": project.get("estimated_timeline"),
                "team_size": project.get("team_size"),
                "budget_constraints": project.get("budget_constraints"),
                "priority_level": project.get("priority_level")
            },
            "metadata": {
                "tags": project.get("tags", []),
                "created_at": project.get("created_at"),
                "status": project.get("status")
            }
        }
    
    def _build_agent_instructions(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Build specific instructions for agent collaboration."""
        return {
            "collaboration_mode": "comprehensive_analysis",
            "focus_areas": [
                "Project architecture and structure",
                "Detailed task breakdown",
                "File and folder organization",
                "Implementation roadmap",
                "Technical specifications"
            ],
            "output_requirements": {
                "project_overview": {
                    "include_file_structure": True,
                    "include_architecture_diagram": True,
                    "include_technical_specs": True,
                    "include_implementation_plan": True
                },
                "task_files": {
                    "minimum_tasks": 10,
                    "maximum_tasks": 20,
                    "include_subtasks": True,
                    "include_dependencies": True,
                    "include_file_references": True,
                    "include_effort_estimates": True
                }
            },
            "quality_standards": {
                "scalability": "Design for scalable, modular architecture",
                "maintainability": "Ensure code maintainability and documentation",
                "best_practices": "Follow industry best practices and patterns",
                "testing": "Include comprehensive testing strategy"
            }
        }
    
    def _get_collaboration_guidelines(self) -> Dict[str, Any]:
        """Get guidelines for agent collaboration."""
        return {
            "collaboration_process": [
                "Agents should discuss and reach consensus on project understanding",
                "Each agent contributes their specialized expertise",
                "Agents should ask clarifying questions and resolve conflicts",
                "Final outputs should reflect collaborative decisions"
            ],
            "communication_style": "Professional, detailed, and constructive",
            "decision_making": "Consensus-based with clear rationale",
            "conflict_resolution": "Discuss alternatives and choose best approach"
        }
    
    def _get_expected_outputs(self) -> Dict[str, Any]:
        """Get expected outputs from agent collaboration."""
        return {
            "project_overview": {
                "format": "Markdown",
                "sections": [
                    "Project Description",
                    "Technical Architecture", 
                    "File and Folder Structure",
                    "Technology Stack",
                    "Implementation Plan",
                    "Deliverables"
                ]
            },
            "task_files": {
                "format": "Markdown",
                "naming_convention": "Task_{number}_{category}.md",
                "required_sections": [
                    "Task Description",
                    "Acceptance Criteria", 
                    "Subtasks",
                    "Dependencies",
                    "File References",
                    "Effort Estimate"
                ]
            }
        }
