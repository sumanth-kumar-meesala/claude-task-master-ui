"""
Pydantic schemas for data validation and serialization.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"





class TemplateType(str, Enum):
    """Template type enumeration."""
    PROJECT = "project"
    WORKFLOW = "workflow"
    PROMPT = "prompt"





# Enhanced Project Models for New Workflow
class ProjectBase(BaseModel):
    """Simplified base project model with core fields only."""
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: str = Field(..., min_length=10, max_length=5000, description="Detailed project description")
    requirements: str = Field(..., min_length=10, description="Comprehensive project requirements")

    # Core fields
    status: ProjectStatus = Field(ProjectStatus.DRAFT, description="Project status")
    tags: List[str] = Field(default_factory=list, description="Project tags for categorization")
    tech_stack: List[str] = Field(default_factory=list, description="Technology stack")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags list."""
        if len(v) > 20:
            raise ValueError("Maximum 20 tags allowed")
        return [tag.strip().lower() for tag in v if tag.strip()]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "E-commerce Platform",
                "description": "A modern e-commerce platform with AI recommendations",
                "requirements": "User authentication, product catalog, shopping cart, payment integration",
                "status": "draft",
                "tags": ["ecommerce", "ai", "web"],
                "metadata": {
                    "priority": "high",
                    "estimated_duration": "3 months"
                },

            }
        }


class ProjectCreate(ProjectBase):
    """Enhanced project creation model."""

    class Config:
        extra = "ignore"  # Allow extra fields to be ignored rather than causing validation errors





# Generated File Models
class GeneratedProjectFile(BaseModel):
    """Model for generated project files."""
    id: str = Field(..., description="File ID")
    project_id: str = Field(..., description="Associated project ID")
    collaboration_session_id: Optional[str] = Field(None, description="Associated collaboration session ID")

    # File details
    file_name: str = Field(..., description="File name")
    file_type: str = Field(..., description="File type (overview, task, etc.)")
    file_path: str = Field(..., description="File path within project structure")
    content: str = Field(..., description="File content")

    # Metadata
    generation_context: Dict[str, Any] = Field(default_factory=dict, description="Context used for generation")
    file_dependencies: List[str] = Field(default_factory=list, description="Dependencies on other files")
    referenced_files: List[str] = Field(default_factory=list, description="Files referenced in this file")

    # Status
    status: str = Field("generated", description="File status")
    version: int = Field(1, description="File version")

    # Timestamps
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


# Project Structure Models
class ProjectStructureNode(BaseModel):
    """Model for project structure nodes (files/folders)."""
    name: str = Field(..., description="Node name")
    type: str = Field(..., description="Node type (file, folder)")
    path: str = Field(..., description="Full path")
    description: Optional[str] = Field(None, description="Node description")
    children: List['ProjectStructureNode'] = Field(default_factory=list, description="Child nodes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProjectStructure(BaseModel):
    """Model for complete project structure."""
    project_id: str = Field(..., description="Associated project ID")
    root_structure: ProjectStructureNode = Field(..., description="Root structure node")
    total_files: int = Field(0, description="Total number of files")
    total_folders: int = Field(0, description="Total number of folders")
    structure_metadata: Dict[str, Any] = Field(default_factory=dict, description="Structure metadata")
    generated_at: Optional[str] = Field(None, description="Generation timestamp")


# Task Models
class TaskDefinition(BaseModel):
    """Model for detailed task definitions."""
    id: str = Field(..., description="Task ID")
    project_id: str = Field(..., description="Associated project ID")
    task_number: int = Field(..., description="Task number")

    # Task details
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Detailed task description")
    category: str = Field(..., description="Task category")
    priority: str = Field("medium", description="Task priority")

    # Technical details
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")
    subtasks: List[Dict[str, Any]] = Field(default_factory=list, description="Subtasks")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    referenced_files: List[str] = Field(default_factory=list, description="Referenced files from project structure")
    affected_components: List[str] = Field(default_factory=list, description="Affected system components")

    # Estimation
    estimated_effort: str = Field(..., description="Estimated effort")
    estimated_duration: Optional[str] = Field(None, description="Estimated duration")
    complexity_level: str = Field("medium", description="Complexity level")

    # Implementation details
    technical_notes: Optional[str] = Field(None, description="Technical implementation notes")
    testing_requirements: Optional[str] = Field(None, description="Testing requirements")
    documentation_requirements: Optional[str] = Field(None, description="Documentation requirements")

    # Metadata
    status: str = Field("pending", description="Task status")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


# Update ProjectStructureNode to handle forward references
ProjectStructureNode.model_rebuild()


class ProjectUpdate(BaseModel):
    """Project update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    requirements: Optional[str] = None
    status: Optional[ProjectStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags list."""
        if v is not None:
            if len(v) > 20:
                raise ValueError("Maximum 20 tags allowed")
            return [tag.strip().lower() for tag in v if tag.strip()]
        return v


class Project(ProjectBase):
    """Complete project model."""
    id: str = Field(..., description="Project ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    session_count: int = Field(0, description="Number of associated sessions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "proj_123456789",
                "name": "E-commerce Platform",
                "description": "A modern e-commerce platform with AI recommendations",
                "requirements": "User authentication, product catalog, shopping cart, payment integration",
                "status": "draft",
                "tags": ["ecommerce", "ai", "web"],
                "metadata": {
                    "priority": "high",
                    "estimated_duration": "3 months"
                },

                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "session_count": 0
            }
        }



    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "sess_123456789",
                "project_id": "proj_123456789",
                "name": "Initial Analysis Session",
                "description": "First analysis of the e-commerce platform requirements",
                "status": "active",

                "metadata": {
                    "user_id": "user_123",
                    "priority": "normal"
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "started_at": "2024-01-01T00:00:00Z",
                "completed_at": None,
                "duration": None
            }
        }


# Template Models
class TemplateBase(BaseModel):
    """Base template model."""
    name: str = Field(..., min_length=1, max_length=200, description="Template name")
    description: Optional[str] = Field(None, max_length=1000, description="Template description")
    type: TemplateType = Field(..., description="Template type")
    content: Dict[str, Any] = Field(..., description="Template content")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    is_public: bool = Field(False, description="Whether template is publicly available")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags list."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return [tag.strip().lower() for tag in v if tag.strip()]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Web Application Template",
                "description": "Standard template for web application projects",
                "type": "project",
                "content": {
                    "sections": ["requirements", "architecture", "implementation"]
                },
                "tags": ["web", "template", "standard"],
                "is_public": True,
                "metadata": {
                    "version": "1.0",
                    "author": "system"
                }
            }
        }


class TemplateCreate(TemplateBase):
    """Template creation model."""

    class Config:
        extra = "ignore"  # Allow extra fields to be ignored rather than causing validation errors


class TemplateUpdate(BaseModel):
    """Template update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    type: Optional[TemplateType] = None
    content: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags list."""
        if v is not None:
            if len(v) > 10:
                raise ValueError("Maximum 10 tags allowed")
            return [tag.strip().lower() for tag in v if tag.strip()]
        return v


class Template(TemplateBase):
    """Complete template model."""
    id: str = Field(..., description="Template ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    usage_count: int = Field(0, description="Number of times template has been used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "tmpl_123456789",
                "name": "Web Application Template",
                "description": "Standard template for web application projects",
                "type": "project",
                "content": {
                    "sections": ["requirements", "architecture", "implementation"]
                },
                "tags": ["web", "template", "standard"],
                "is_public": True,
                "metadata": {
                    "version": "1.0",
                    "author": "system"
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "usage_count": 0
            }
        }


# Project Files Models
class ProjectFileType(str, Enum):
    """Project file types."""
    PROJECT_OVERVIEW = "project_overview"
    TASK_FILE = "task_file"
    TASKS_INDEX = "tasks_index"
    GENERATED_FILE = "generated_file"


class ProjectFileStatus(str, Enum):
    """Project file status."""
    GENERATED = "generated"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    ARCHIVED = "archived"


class ProjectFileMetadata(BaseModel):
    """Project file metadata."""
    generation_context: Dict[str, Any] = Field(default_factory=dict, description="Context used for generation")
    file_size: Optional[int] = Field(None, description="File size in characters")
    task_number: Optional[int] = Field(None, description="Task number for task files")
    is_primary: bool = Field(False, description="Whether this is the primary file of its type")


class ProjectFileBase(BaseModel):
    """Base project file model."""
    project_id: str = Field(..., description="Associated project ID")
    session_id: Optional[str] = Field(None, description="Associated session ID")
    file_type: ProjectFileType = Field(..., description="Type of file")
    file_name: str = Field(..., min_length=1, max_length=255, description="File name")
    content: str = Field(..., description="File content")
    metadata: ProjectFileMetadata = Field(default_factory=ProjectFileMetadata, description="File metadata")
    status: ProjectFileStatus = Field(ProjectFileStatus.GENERATED, description="File status")

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proj_123456789",

                "session_id": "sess_123456789",
                "file_type": "project_overview",
                "file_name": "ProjectOverview.md",
                "content": "# Project Overview\n\nThis is a comprehensive project overview...",
                "metadata": {
                    "generation_context": {"project_name": "E-commerce Platform"},
                    "file_size": 2500,
                    "is_primary": True
                },
                "status": "generated"
            }
        }


class ProjectFileCreate(ProjectFileBase):
    """Project file creation model."""

    class Config:
        extra = "ignore"  # Allow extra fields to be ignored rather than causing validation errors


class ProjectFileUpdate(BaseModel):
    """Project file update model."""
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    metadata: Optional[ProjectFileMetadata] = None
    status: Optional[ProjectFileStatus] = None


class ProjectFile(ProjectFileBase):
    """Complete project file model."""
    id: str = Field(..., description="File ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "file_123456789",
                "project_id": "proj_123456789",

                "session_id": "sess_123456789",
                "file_type": "project_overview",
                "file_name": "ProjectOverview.md",
                "content": "# Project Overview\n\nThis is a comprehensive project overview...",
                "metadata": {
                    "generation_context": {"project_name": "E-commerce Platform"},
                    "file_size": 2500,
                    "is_primary": True
                },
                "status": "generated",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
