"""
Task Master Service Integration

This service integrates the claude-task-master functionality with our FastAPI backend,
enabling PRD parsing and task generation using the Node.js task-master-ai package.
"""

import os
import json
import tempfile
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TaskMasterService:
    """Service for integrating with claude-task-master functionality."""
    
    def __init__(self):
        self.task_master_path = self._get_task_master_path()
        self.node_env = self._setup_node_environment()
    
    def _get_task_master_path(self) -> str:
        """Get the path to the task-master-ai executable."""
        # Path to the installed task-master-ai in node_modules
        backend_dir = Path(__file__).parent.parent.parent
        task_master_path = backend_dir / "node_modules" / "task-master-ai" / "scripts" / "dev.js"
        
        if not task_master_path.exists():
            raise FileNotFoundError(f"task-master-ai not found at {task_master_path}")
        
        return str(task_master_path)
    
    def _setup_node_environment(self) -> Dict[str, str]:
        """Setup environment variables for Node.js execution."""
        env = os.environ.copy()
        
        # Add Gemini API key from our settings
        if settings.GEMINI_API_KEY:
            env["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
            env["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
        
        # Add other API keys if available
        api_keys = [
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY", 
            "PERPLEXITY_API_KEY",
            "XAI_API_KEY",
            "OPENROUTER_API_KEY",
            "MISTRAL_API_KEY"
        ]
        
        for key in api_keys:
            if hasattr(settings, key) and getattr(settings, key):
                env[key] = getattr(settings, key)
        
        return env

    async def _update_config_for_gemini(self, config_file: str) -> None:
        """Update task-master config to use Gemini models."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Update models to use Google Gemini (using flash model to avoid quota issues)
            config["models"] = {
                "main": {
                    "provider": "google",
                    "modelId": "gemini-2.5-flash-preview-05-20",
                    "maxTokens": 120000 ,
                    "temperature": 0.2
                },
                "research": {
                    "provider": "google",
                    "modelId": "gemini-2.5-flash-preview-05-20",
                    "maxTokens": 120000,
                    "temperature": 0.1
                },
                "fallback": {
                    "provider": "google",
                    "modelId": "gemini-2.5-flash",
                    "maxTokens": 120000,
                    "temperature": 0.1
                }
            }

            # Write updated config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"Updated config to use Gemini models: {config_file}")

        except Exception as e:
            logger.error(f"Failed to update config for Gemini: {e}")

    async def _create_env_file(self, project_path: str) -> None:
        """Create .env file with API keys in the project directory."""
        try:
            env_file = os.path.join(project_path, ".env")
            gemini_api_key = settings.GEMINI_API_KEY

            if not gemini_api_key:
                logger.warning("GEMINI_API_KEY not found in settings")
                return

            env_content = f"""# Task Master AI Environment Variables
GOOGLE_API_KEY={gemini_api_key}
GEMINI_API_KEY={gemini_api_key}
"""

            with open(env_file, 'w') as f:
                f.write(env_content)

            logger.info(f"Created .env file with API keys: {env_file}")

        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")

    async def initialize_project(self, project_path: str, project_name: str = None) -> Dict[str, Any]:
        """Initialize a task-master project in the given directory."""
        try:
            # Create project directory if it doesn't exist
            os.makedirs(project_path, exist_ok=True)

            # Check if already initialized
            config_file = os.path.join(project_path, ".taskmaster", "config.json")
            if os.path.exists(config_file):
                logger.info(f"Project already initialized at {project_path}")
                # Update config to use Gemini models
                await self._update_config_for_gemini(config_file)
                # Ensure .env file exists
                await self._create_env_file(project_path)
                return {
                    "success": True,
                    "message": "Project already initialized",
                    "project_path": project_path
                }

            # Run task-master init
            cmd = ["node", self.task_master_path, "init", "--yes"]
            if project_name:
                cmd.extend(["--name", project_name])

            result = await self._run_command(cmd, cwd=project_path)

            if result["returncode"] == 0:
                # Verify initialization was successful
                if os.path.exists(config_file):
                    # Update config to use Gemini models
                    await self._update_config_for_gemini(config_file)

                    # Create .env file with API keys
                    await self._create_env_file(project_path)

                    logger.info(f"Successfully initialized task-master project at {project_path}")
                    return {
                        "success": True,
                        "message": "Project initialized successfully",
                        "project_path": project_path
                    }
                else:
                    logger.error(f"Initialization appeared successful but config file not found")
                    return {
                        "success": False,
                        "error": "Config file not created",
                        "message": "Initialization incomplete"
                    }
            else:
                logger.error(f"Failed to initialize project: {result['stderr']}")
                return {
                    "success": False,
                    "error": result["stderr"],
                    "message": "Failed to initialize project"
                }

        except Exception as e:
            logger.error(f"Error initializing project: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error initializing project"
            }
    
    async def parse_prd(
        self,
        prd_content: str,
        project_path: str,
        num_tasks: int = 10,
        research: bool = False,
        force: bool = False,
        append: bool = False
    ) -> Dict[str, Any]:
        """Parse a PRD and generate tasks using task-master."""
        try:
            # Ensure project is initialized first
            config_file = os.path.join(project_path, ".taskmaster", "config.json")
            if not os.path.exists(config_file):
                logger.info(f"Project not initialized, initializing now: {project_path}")
                init_result = await self.initialize_project(project_path)
                if not init_result["success"]:
                    return {
                        "success": False,
                        "error": f"Failed to initialize project: {init_result.get('error', 'Unknown error')}",
                        "message": "Project initialization failed"
                    }

            # Create temporary PRD file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as prd_file:
                prd_file.write(prd_content)
                prd_file_path = prd_file.name

            try:
                # Ensure docs directory exists
                taskmaster_dir = os.path.join(project_path, ".taskmaster")
                docs_dir = os.path.join(taskmaster_dir, "docs")
                os.makedirs(docs_dir, exist_ok=True)

                # Copy PRD to project directory
                project_prd_path = os.path.join(docs_dir, "prd.txt")
                with open(project_prd_path, 'w') as f:
                    f.write(prd_content)

                # Verify file was created
                if not os.path.exists(project_prd_path):
                    raise Exception(f"Failed to create PRD file at {project_prd_path}")

                # Build command - use relative path from project directory
                relative_prd_path = os.path.relpath(project_prd_path, project_path)
                cmd = ["node", self.task_master_path, "parse-prd", relative_prd_path]
                cmd.extend(["--num-tasks", str(num_tasks)])

                logger.info(f"Running command: {' '.join(cmd)} in directory: {project_path}")

                if research:
                    cmd.append("--research")
                if force:
                    cmd.append("--force")
                if append:
                    cmd.append("--append")

                # Run the command
                result = await self._run_command(cmd, cwd=project_path)
                
                if result["returncode"] == 0:
                    # Read generated tasks from the correct location
                    tasks_file = os.path.join(project_path, ".taskmaster", "tasks", "tasks.json")
                    if os.path.exists(tasks_file):
                        with open(tasks_file, 'r') as f:
                            tasks_data = json.load(f)

                        # Generate individual markdown files for each task
                        logger.info("Generating individual markdown files for tasks...")
                        generate_result = await self.generate_task_files(project_path)

                        if not generate_result["success"]:
                            logger.warning(f"Failed to generate markdown files: {generate_result.get('error', 'Unknown error')}")
                            # Continue anyway since we have the JSON data

                        logger.info(f"Successfully parsed PRD and generated {len(tasks_data.get('master', {}).get('tasks', []))} tasks")
                        return {
                            "success": True,
                            "tasks": tasks_data,
                            "message": f"Successfully generated {len(tasks_data.get('master', {}).get('tasks', []))} tasks",
                            "project_path": project_path,
                            "prd_path": project_prd_path,
                            "markdown_files_generated": generate_result.get("success", False)
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Tasks file not generated",
                            "message": "PRD parsing completed but no tasks file found"
                        }
                else:
                    logger.error(f"Failed to parse PRD: {result['stderr']}")
                    return {
                        "success": False,
                        "error": result["stderr"],
                        "message": "Failed to parse PRD"
                    }
                    
            finally:
                # Clean up temporary file
                os.unlink(prd_file_path)
                
        except Exception as e:
            logger.error(f"Error parsing PRD: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error parsing PRD"
            }
    
    async def list_tasks(self, project_path: str) -> Dict[str, Any]:
        """List all tasks in the project."""
        try:
            cmd = ["node", self.task_master_path, "list"]
            result = await self._run_command(cmd, cwd=project_path)
            
            if result["returncode"] == 0:
                # Also read the tasks.json file for structured data
                tasks_file = os.path.join(project_path, ".taskmaster", "tasks", "tasks.json")
                if os.path.exists(tasks_file):
                    with open(tasks_file, 'r') as f:
                        tasks_data = json.load(f)

                    return {
                        "success": True,
                        "tasks": tasks_data,
                        "output": result["stdout"],
                        "message": "Tasks retrieved successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "No tasks file found",
                        "message": "No tasks found in project"
                    }
            else:
                return {
                    "success": False,
                    "error": result["stderr"],
                    "message": "Failed to list tasks"
                }
                
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error listing tasks"
            }
    
    async def generate_task_files(self, project_path: str) -> Dict[str, Any]:
        """Generate individual markdown files for each task."""
        try:
            cmd = ["node", self.task_master_path, "generate"]
            result = await self._run_command(cmd, cwd=project_path)

            if result["returncode"] == 0:
                return {
                    "success": True,
                    "output": result["stdout"],
                    "message": "Task files generated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result["stderr"],
                    "message": "Failed to generate task files"
                }

        except Exception as e:
            logger.error(f"Error generating task files: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error generating task files"
            }

    async def get_task_markdown_files(self, project_path: str) -> Dict[str, Any]:
        """Get all generated markdown files for tasks."""
        try:
            tasks_dir = os.path.join(project_path, ".taskmaster", "tasks")
            if not os.path.exists(tasks_dir):
                return {
                    "success": False,
                    "error": "Tasks directory not found",
                    "files": []
                }

            markdown_files = []
            for filename in os.listdir(tasks_dir):
                if filename.endswith('.md') and filename != 'README.md':
                    file_path = os.path.join(tasks_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Extract task ID from filename (assuming format like "task-1.md" or "1.md")
                        task_id = None
                        if filename.startswith('task-'):
                            task_id = filename.replace('task-', '').replace('.md', '')
                        elif filename.replace('.md', '').isdigit():
                            task_id = filename.replace('.md', '')

                        markdown_files.append({
                            "filename": filename,
                            "task_id": task_id,
                            "content": content,
                            "file_path": file_path
                        })
                    except Exception as e:
                        logger.warning(f"Failed to read markdown file {filename}: {e}")

            return {
                "success": True,
                "files": markdown_files,
                "count": len(markdown_files)
            }

        except Exception as e:
            logger.error(f"Error getting task markdown files: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "files": []
            }

    async def get_next_task(self, project_path: str) -> Dict[str, Any]:
        """Get the next task to work on."""
        try:
            cmd = ["node", self.task_master_path, "next"]
            result = await self._run_command(cmd, cwd=project_path)

            if result["returncode"] == 0:
                return {
                    "success": True,
                    "output": result["stdout"],
                    "message": "Next task retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result["stderr"],
                    "message": "Failed to get next task"
                }

        except Exception as e:
            logger.error(f"Error getting next task: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error getting next task"
            }
    
    async def _run_command(self, cmd: List[str], cwd: str = None) -> Dict[str, Any]:
        """Run a command asynchronously and return the result."""
        try:
            logger.info(f"Running command: {' '.join(cmd)} in directory: {cwd}")

            # Use subprocess.run with asyncio.to_thread for Windows compatibility
            import subprocess

            def run_sync():
                return subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    env=self.node_env,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

            # Run the subprocess in a thread to avoid blocking
            process_result = await asyncio.to_thread(run_sync)

            result = {
                "returncode": process_result.returncode,
                "stdout": process_result.stdout or "",
                "stderr": process_result.stderr or ""
            }

            logger.info(f"Command completed with return code: {process_result.returncode}")
            if process_result.returncode != 0:
                logger.error(f"Command failed with stderr: {result['stderr'][:500]}...")

            return result

        except Exception as e:
            logger.error(f"Exception running command {' '.join(cmd)}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": str(e)
            }


# Global instance
task_master_service = TaskMasterService()
