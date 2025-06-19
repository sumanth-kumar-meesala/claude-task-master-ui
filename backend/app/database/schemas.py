"""
JSON schemas for database validation.
"""

from typing import Dict, Any

# Enhanced Project schema for new workflow
PROJECT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "description": {
            "type": "string",
            "minLength": 10,
            "maxLength": 5000
        },
        "requirements": {
            "type": "string",
            "minLength": 10
        },

        # Technical specifications
        "tech_stack": {
            "type": "array",
            "items": {"type": "string"}
        },

        "status": {
            "type": "string",
            "enum": ["draft", "active", "completed", "archived", "cancelled"]
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 20
        },
        "metadata": {
            "type": "object"
        },

        "is_ready_for_orchestration": {"type": "boolean"},
        "orchestration_preferences": {"type": "object"},
        "selected_agents": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "custom_prompt": {"type": ["string", "null"]},
                    "custom_role": {"type": ["string", "null"]},
                    "custom_goal": {"type": ["string", "null"]},
                    "is_active": {"type": "boolean"},
                    "added_at": {"type": "string"},
                    "custom_config": {"type": "object"}
                },
                "required": ["agent_id", "is_active", "added_at"]
            }
        },

        "file_structure": {
            "type": "object"
        },
        "tasks": {
            "type": "array"
        },
        "session_data": {
            "type": "object"
        },
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"},
        "session_count": {
            "type": "integer",
            "minimum": 0
        },

        # Task Master integration fields
        "task_master_initialized": {"type": "boolean"},
        "task_master_path": {"type": ["string", "null"]},
        "tasks_generated": {"type": "boolean"},
        "tasks_count": {"type": "integer", "minimum": 0},
        "last_task_generation": {"type": ["string", "null"]},
        "task_master_config": {
            "type": "object",
            "properties": {
                "use_research": {"type": "boolean"},
                "default_num_tasks": {"type": "integer", "minimum": 1, "maximum": 50},
                "last_prd_content": {"type": ["string", "null"]},
                "generation_history": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timestamp": {"type": "string"},
                            "num_tasks": {"type": "integer"},
                            "research_used": {"type": "boolean"},
                            "success": {"type": "boolean"}
                        }
                    }
                }
            }
        }
    },
    "required": ["id", "name", "status", "created_at", "updated_at"],
    "additionalProperties": True
}



# Project Files schema
PROJECT_FILES_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "project_id": {"type": "string"},
        "orchestration_id": {"type": ["string", "null"]},
        "session_id": {"type": ["string", "null"]},
        "file_type": {
            "type": "string",
            "enum": ["project_overview", "task_file", "tasks_index", "generated_file"]
        },
        "file_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "content": {
            "type": "string"
        },
        "metadata": {
            "type": "object",
            "properties": {
                "agents_used": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "generation_context": {"type": "object"},
                "file_size": {"type": "integer"},
                "task_number": {"type": ["integer", "null"]},
                "is_primary": {"type": "boolean"}
            }
        },
        "status": {
            "type": "string",
            "enum": ["generated", "reviewed", "approved", "archived"],
            "default": "generated"
        },
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"}
    },
    "required": ["id", "project_id", "file_type", "file_name", "content", "created_at", "updated_at"],
    "additionalProperties": False
}

# Template schema
TEMPLATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "description": {
            "type": ["string", "null"],
            "maxLength": 1000
        },
        "type": {
            "type": "string",
            "enum": ["project", "agent", "workflow", "prompt"]
        },
        "content": {
            "type": "object"
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 10
        },
        "is_public": {"type": "boolean"},
        "metadata": {
            "type": "object"
        },
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"},
        "usage_count": {
            "type": "integer",
            "minimum": 0
        }
    },
    "required": ["id", "name", "type", "content", "created_at", "updated_at"],
    "additionalProperties": False
}

# Orchestration sessions schema
ORCHESTRATION_SESSIONS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "project_id": {"type": "string"},
        "name": {"type": ["string", "null"]},
        "description": {"type": ["string", "null"]},
        "status": {"type": "string"},
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"},
        "started_at": {"type": ["string", "null"]},
        "completed_at": {"type": ["string", "null"]},
        "duration": {"type": ["number", "null"]},
        "agent_results": {
            "type": "object"
        },
        "metadata": {
            "type": "object",
            "properties": {
                "orchestration_data": {
                    "type": "object",
                    "properties": {
                        "project_context": {"type": "object"},
                        "selected_agents": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "phase": {"type": "string"},
                        "messages": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "type": {"type": "string"},
                                    "sender_id": {"type": "string"},
                                    "recipient_id": {"type": ["string", "null"]},
                                    "content": {"type": "string"},
                                    "timestamp": {"type": "string"},
                                    "thread_id": {"type": ["string", "null"]}
                                },
                                "required": ["id", "type", "sender_id", "content", "timestamp"]
                            }
                        },
                        "agent_states": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "agent_id": {"type": "string"},
                                    "status": {"type": "string"},
                                    "current_task": {"type": ["string", "null"]},
                                    "progress": {"type": "number"},
                                    "last_activity": {"type": "string"},
                                    "current_output": {"type": ["string", "null"]},
                                    "error_message": {"type": ["string", "null"]}
                                },
                                "required": ["agent_id", "status", "progress", "last_activity"]
                            }
                        },
                        "generated_files": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "final_outputs": {"type": "object"},
                        "is_active": {"type": "boolean"}
                    },
                    "required": ["project_context", "selected_agents", "phase", "messages", "agent_states", "generated_files", "final_outputs", "is_active"]
                }
            }
        }
    },
    "required": ["id", "project_id", "status", "created_at", "updated_at", "agent_results", "metadata"],
    "additionalProperties": False
}

# Agent Collaboration Sessions Schema
COLLABORATION_SESSIONS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "project_id": {"type": "string"},
        "session_name": {"type": "string"},
        "phase": {"type": "string"},
        "status": {"type": "string"},
        "participating_agents": {
            "type": "array",
            "items": {"type": "string"}
        },
        "collaboration_messages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "message": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "message_type": {"type": "string"}
                },
                "required": ["agent_id", "message", "timestamp", "message_type"]
            }
        },
        "shared_context": {"type": "object"},
        "decisions_made": {
            "type": "array",
            "items": {"type": "object"}
        },
        "open_questions": {
            "type": "array",
            "items": {"type": "object"}
        },
        "current_focus": {"type": ["string", "null"]},
        "progress_percentage": {"type": "number"},
        "estimated_completion": {"type": ["string", "null"]},
        "started_at": {"type": ["string", "null"]},
        "updated_at": {"type": ["string", "null"]},
        "completed_at": {"type": ["string", "null"]},
        "created_at": {"type": ["string", "null"]}
    },
    "required": ["id", "project_id", "session_name", "phase", "status"],
    "additionalProperties": False
}

# Generated Project Files Schema
GENERATED_FILES_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "project_id": {"type": "string"},
        "collaboration_session_id": {"type": ["string", "null"]},
        "file_name": {"type": "string"},
        "file_type": {"type": "string"},
        "file_path": {"type": "string"},
        "content": {"type": "string"},
        "generated_by_agents": {
            "type": "array",
            "items": {"type": "string"}
        },
        "generation_context": {"type": "object"},
        "file_dependencies": {
            "type": "array",
            "items": {"type": "string"}
        },
        "referenced_files": {
            "type": "array",
            "items": {"type": "string"}
        },
        "status": {"type": "string"},
        "version": {"type": "integer"},
        "created_at": {"type": ["string", "null"]},
        "updated_at": {"type": ["string", "null"]}
    },
    "required": ["id", "project_id", "file_name", "file_type", "file_path", "content"],
    "additionalProperties": False
}

# Project Structure Schema
PROJECT_STRUCTURE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "project_id": {"type": "string"},
        "root_structure": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "path": {"type": "string"},
                "description": {"type": ["string", "null"]},
                "children": {"type": "array"},
                "metadata": {"type": "object"}
            },
            "required": ["name", "type", "path"]
        },
        "total_files": {"type": "integer"},
        "total_folders": {"type": "integer"},
        "structure_metadata": {"type": "object"},
        "generated_at": {"type": ["string", "null"]}
    },
    "required": ["id", "project_id", "root_structure"],
    "additionalProperties": False
}

# Task Definitions Schema
TASK_DEFINITIONS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "project_id": {"type": "string"},
        "task_number": {"type": "integer"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "category": {"type": "string"},
        "priority": {"type": "string"},
        "acceptance_criteria": {
            "type": "array",
            "items": {"type": "string"}
        },
        "subtasks": {
            "type": "array",
            "items": {"type": "object"}
        },
        "dependencies": {
            "type": "array",
            "items": {"type": "string"}
        },
        "referenced_files": {
            "type": "array",
            "items": {"type": "string"}
        },
        "affected_components": {
            "type": "array",
            "items": {"type": "string"}
        },
        "estimated_effort": {"type": "string"},
        "estimated_duration": {"type": ["string", "null"]},
        "complexity_level": {"type": "string"},
        "technical_notes": {"type": ["string", "null"]},
        "testing_requirements": {"type": ["string", "null"]},
        "documentation_requirements": {"type": ["string", "null"]},
        "created_by_agents": {
            "type": "array",
            "items": {"type": "string"}
        },
        "status": {"type": "string"},
        "created_at": {"type": ["string", "null"]}
    },
    "required": ["id", "project_id", "task_number", "title", "description", "category", "estimated_effort"],
    "additionalProperties": False
}

# Schema mapping for different database types
SCHEMAS = {
    "projects": PROJECT_SCHEMA,
    "templates": TEMPLATE_SCHEMA,
    "project_files": PROJECT_FILES_SCHEMA,
    "orchestration_sessions": ORCHESTRATION_SESSIONS_SCHEMA,
    "collaboration_sessions": COLLABORATION_SESSIONS_SCHEMA,
    "generated_files": GENERATED_FILES_SCHEMA,
    "project_structure": PROJECT_STRUCTURE_SCHEMA,
    "task_definitions": TASK_DEFINITIONS_SCHEMA
}


def get_schema(db_type: str) -> Dict[str, Any]:
    """
    Get JSON schema for a specific database type.

    Args:
        db_type: Type of database (projects, templates, project_files)

    Returns:
        JSON schema dictionary

    Raises:
        ValueError: If db_type is not supported
    """
    if db_type not in SCHEMAS:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    return SCHEMAS[db_type]


def validate_schema_compatibility(data: Dict[str, Any], db_type: str) -> bool:
    """
    Check if data is compatible with the schema for a database type.
    
    Args:
        data: Data to validate
        db_type: Type of database
        
    Returns:
        True if compatible, False otherwise
    """
    try:
        schema = get_schema(db_type)
        from jsonschema import validate
        validate(instance=data, schema=schema)
        return True
    except Exception:
        return False
