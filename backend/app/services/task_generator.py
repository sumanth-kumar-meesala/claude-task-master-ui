"""
Task Generator Service.

This service generates 10-20 detailed task files with subtasks, dependencies,
effort estimates, and references to existing files from ProjectOverview.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.database.tinydb_handler import get_task_definitions_db, get_generated_files_db
from app.models.schemas import TaskDefinition, GeneratedProjectFile
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class TaskGenerator:
    """Service for generating detailed project tasks."""
    
    def __init__(self):
        """Initialize the task generator."""
        self.task_definitions_db = get_task_definitions_db()
        self.generated_files_db = get_generated_files_db()
        logger.info("Task Generator initialized")
    
    async def generate_project_tasks(
        self, 
        project_id: str, 
        collaboration_results: Dict[str, Any],
        project_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate 10-20 detailed task files based on collaboration results and project structure.
        
        Args:
            project_id: Project ID
            collaboration_results: Results from agent collaboration
            project_structure: Generated project structure
            
        Returns:
            Generated tasks information
        """
        try:
            logger.info(f"Generating project tasks for project {project_id}")
            
            # Extract collaboration insights
            final_consensus = collaboration_results["final_consensus"]
            
            # Generate task breakdown
            task_breakdown = await self._generate_task_breakdown(
                project_id, final_consensus, project_structure
            )
            
            # Generate individual task files
            task_files = []
            task_definitions = []
            
            for i, task_data in enumerate(task_breakdown["tasks"], 1):
                # Generate detailed task definition
                task_definition = await self._create_task_definition(
                    project_id, i, task_data, project_structure
                )
                
                # Generate task file content
                task_file_content = await self._generate_task_file_content(
                    task_definition, project_structure
                )
                
                # Save task file
                task_file_id = await self._save_task_file(
                    project_id, task_definition, task_file_content, 
                    collaboration_results["session_id"]
                )
                
                task_definitions.append(task_definition)
                task_files.append({
                    "file_id": task_file_id,
                    "task_number": i,
                    "title": task_definition["title"],
                    "category": task_definition["category"],
                    "file_name": f"Task_{i:02d}_{task_definition['category']}.md"
                })
            
            # Generate task index file
            index_file_id = await self._generate_task_index(
                project_id, task_definitions, collaboration_results["session_id"]
            )
            
            return {
                "task_files": task_files,
                "task_definitions": task_definitions,
                "index_file_id": index_file_id,
                "total_tasks": len(task_files),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate project tasks: {e}")
            raise
    
    async def _generate_task_breakdown(
        self, 
        project_id: str, 
        final_consensus: Dict[str, Any],
        project_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive task breakdown.
        
        Args:
            project_id: Project ID
            final_consensus: Final consensus from collaboration
            project_structure: Project structure
            
        Returns:
            Task breakdown with 10-20 tasks
        """
        try:
            logger.info(f"Generating task breakdown for {project_id}")
            
            # Create task breakdown prompt
            breakdown_prompt = self._create_task_breakdown_prompt(
                final_consensus, project_structure
            )
            
            # Create task planning agent if not exists
            task_planner_id = "task_planner"
            if task_planner_id not in self.crew_service.agents:
                self.crew_service.create_agent(
                    name=task_planner_id,
                    role="Senior Project Task Planner",
                    goal="Create detailed, actionable task breakdowns for software projects",
                    backstory="Expert in project management, task decomposition, and agile development practices.",
                    verbose=True
                )
            
            # Create task breakdown task
            breakdown_task = self.crew_service.create_task(
                description=breakdown_prompt,
                agent=self.crew_service.agents[task_planner_id],
                expected_output="Detailed JSON array of 10-20 tasks with all required fields and dependencies."
            )
            
            # Execute task breakdown
            crew_name = f"task_breakdown_{project_id}"
            crew = self.crew_service.create_crew(
                name=crew_name,
                agents=[self.crew_service.agents[task_planner_id]],
                tasks=[breakdown_task],
                verbose=True
            )
            
            result = await self.crew_service.execute_crew(
                crew_name,
                inputs={
                    "project_id": project_id,
                    "consensus": final_consensus,
                    "structure": project_structure
                }
            )
            
            # Process breakdown result
            breakdown_output = result.get("result", "")
            if hasattr(breakdown_output, 'raw'):
                breakdown_output = str(breakdown_output.raw)
            
            # Parse task breakdown
            task_breakdown = self._parse_task_breakdown(breakdown_output)
            
            logger.info(f"Generated {len(task_breakdown['tasks'])} tasks for project {project_id}")
            return task_breakdown
            
        except Exception as e:
            logger.error(f"Error generating task breakdown: {e}")
            raise
    
    def _create_task_breakdown_prompt(
        self, 
        final_consensus: Dict[str, Any], 
        project_structure: Dict[str, Any]
    ) -> str:
        """Create prompt for task breakdown generation."""
        return f"""
# Detailed Task Breakdown Generation

Based on the collaboration results and project structure, create a comprehensive task breakdown with 10-20 detailed tasks.

## Collaboration Results
{final_consensus}

## Project Structure
{project_structure}

## Task Requirements
Generate 10-20 tasks that cover:
1. **Setup and Configuration** - Environment setup, dependencies, configuration
2. **Core Architecture** - Basic structure, core modules, foundational components
3. **Feature Development** - Main features and functionality
4. **Integration** - API integration, database integration, third-party services
5. **User Interface** - UI components, user experience, frontend development
6. **Testing** - Unit tests, integration tests, end-to-end tests
7. **Documentation** - Code documentation, user guides, API documentation
8. **Deployment** - Build process, deployment configuration, CI/CD
9. **Quality Assurance** - Code review, performance optimization, security
10. **Finalization** - Final testing, bug fixes, release preparation

## Task Format
Each task must include:
```json
{{
  "title": "Clear, actionable task title",
  "description": "Detailed description of what needs to be done",
  "category": "setup|architecture|feature|integration|ui|testing|documentation|deployment|qa|finalization",
  "priority": "high|medium|low",
  "acceptance_criteria": ["Specific criteria 1", "Specific criteria 2"],
  "subtasks": [
    {{
      "title": "Subtask title",
      "description": "Subtask description",
      "estimated_hours": 2
    }}
  ],
  "dependencies": ["Task titles this depends on"],
  "referenced_files": ["Files from project structure this task affects"],
  "affected_components": ["System components this task impacts"],
  "estimated_effort": "X hours/days",
  "complexity_level": "low|medium|high",
  "technical_notes": "Implementation guidance and technical considerations",
  "testing_requirements": "Testing approach for this task",
  "documentation_requirements": "Documentation needed for this task"
}}
```

## Guidelines
- Ensure tasks are actionable and specific
- Include proper dependencies and sequencing
- Reference actual files and folders from the project structure
- Provide realistic effort estimates
- Include comprehensive subtasks for complex tasks
- Ensure tasks support scalable, modular development
- Cover all aspects of the project from setup to deployment

## Output Format
Provide a JSON array of 10-20 tasks following the exact format above.

Generate comprehensive tasks that will enable complete project implementation.
"""
    
    def _parse_task_breakdown(self, breakdown_output: str) -> Dict[str, Any]:
        """Parse task breakdown from agent output."""
        try:
            import json
            import re
            
            # Try to extract JSON array from the output
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', breakdown_output, re.DOTALL)
            if json_match:
                tasks_json = json_match.group(1)
                tasks = json.loads(tasks_json)
            else:
                # Try to parse the entire output as JSON
                tasks = json.loads(breakdown_output)
            
            # Ensure we have a list
            if not isinstance(tasks, list):
                tasks = [tasks] if isinstance(tasks, dict) else []
            
            # Validate task count (10-20 tasks)
            if len(tasks) < 10:
                logger.warning(f"Generated only {len(tasks)} tasks, expected 10-20")
            elif len(tasks) > 20:
                logger.warning(f"Generated {len(tasks)} tasks, truncating to 20")
                tasks = tasks[:20]
            
            return {
                "tasks": tasks,
                "total_tasks": len(tasks),
                "categories": list(set(task.get("category", "unknown") for task in tasks))
            }
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse task breakdown as JSON, creating fallback tasks")
            return self._create_fallback_tasks()
    
    def _create_fallback_tasks(self) -> Dict[str, Any]:
        """Create fallback tasks if parsing fails."""
        fallback_tasks = [
            {
                "title": "Project Setup and Environment Configuration",
                "description": "Set up development environment and project structure",
                "category": "setup",
                "priority": "high",
                "acceptance_criteria": ["Development environment is configured", "Project dependencies are installed"],
                "subtasks": [{"title": "Install dependencies", "description": "Install all required packages", "estimated_hours": 2}],
                "dependencies": [],
                "referenced_files": ["package.json", "requirements.txt"],
                "affected_components": ["Development Environment"],
                "estimated_effort": "4 hours",
                "complexity_level": "low",
                "technical_notes": "Follow project setup guidelines",
                "testing_requirements": "Verify environment setup",
                "documentation_requirements": "Document setup process"
            },
            {
                "title": "Core Architecture Implementation",
                "description": "Implement basic project architecture and core modules",
                "category": "architecture",
                "priority": "high",
                "acceptance_criteria": ["Core modules are implemented", "Architecture follows design patterns"],
                "subtasks": [{"title": "Create core modules", "description": "Implement foundational modules", "estimated_hours": 8}],
                "dependencies": ["Project Setup and Environment Configuration"],
                "referenced_files": ["src/", "src/core/"],
                "affected_components": ["Core Architecture"],
                "estimated_effort": "12 hours",
                "complexity_level": "medium",
                "technical_notes": "Follow architectural patterns",
                "testing_requirements": "Unit tests for core modules",
                "documentation_requirements": "Architecture documentation"
            }
        ]
        
        return {
            "tasks": fallback_tasks,
            "total_tasks": len(fallback_tasks),
            "categories": ["setup", "architecture"]
        }
    
    async def _create_task_definition(
        self, 
        project_id: str, 
        task_number: int, 
        task_data: Dict[str, Any],
        project_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create detailed task definition.
        
        Args:
            project_id: Project ID
            task_number: Task number
            task_data: Task data from breakdown
            project_structure: Project structure
            
        Returns:
            Detailed task definition
        """
        try:
            task_id = str(uuid.uuid4())
            
            # Create comprehensive task definition
            task_definition = {
                "id": task_id,
                "project_id": project_id,
                "task_number": task_number,
                "title": task_data.get("title", f"Task {task_number}"),
                "description": task_data.get("description", ""),
                "category": task_data.get("category", "general"),
                "priority": task_data.get("priority", "medium"),
                "acceptance_criteria": task_data.get("acceptance_criteria", []),
                "subtasks": task_data.get("subtasks", []),
                "dependencies": task_data.get("dependencies", []),
                "referenced_files": task_data.get("referenced_files", []),
                "affected_components": task_data.get("affected_components", []),
                "estimated_effort": task_data.get("estimated_effort", "TBD"),
                "estimated_duration": self._calculate_duration(task_data.get("estimated_effort", "")),
                "complexity_level": task_data.get("complexity_level", "medium"),
                "technical_notes": task_data.get("technical_notes", ""),
                "testing_requirements": task_data.get("testing_requirements", ""),
                "documentation_requirements": task_data.get("documentation_requirements", ""),
                "created_by_agents": ["task_planner"],
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Save task definition to database
            self.task_definitions_db.insert(task_definition)
            
            return task_definition
            
        except Exception as e:
            logger.error(f"Error creating task definition: {e}")
            raise
    
    def _calculate_duration(self, effort_estimate: str) -> Optional[str]:
        """Calculate duration from effort estimate."""
        try:
            import re
            
            # Extract numbers from effort estimate
            numbers = re.findall(r'\d+', effort_estimate.lower())
            if not numbers:
                return None
            
            hours = int(numbers[0])
            
            if "day" in effort_estimate.lower():
                hours *= 8  # Assume 8 hours per day
            
            # Convert to duration estimate
            if hours <= 8:
                return f"{hours} hours"
            elif hours <= 40:
                days = hours / 8
                return f"{days:.1f} days"
            else:
                weeks = hours / 40
                return f"{weeks:.1f} weeks"
                
        except:
            return None

    async def _generate_task_file_content(
        self,
        task_definition: Dict[str, Any],
        project_structure: Dict[str, Any]
    ) -> str:
        """
        Generate detailed task file content in markdown format with comprehensive checklists.

        Args:
            task_definition: Task definition
            project_structure: Project structure

        Returns:
            Task file content in markdown with checklists
        """
        try:
            # Create task file content
            content = f"""# Task {task_definition['task_number']:02d}: {task_definition['title']}

## Overview
**Category:** {task_definition['category'].title()}
**Priority:** {task_definition['priority'].title()}
**Complexity:** {task_definition['complexity_level'].title()}
**Estimated Effort:** {task_definition['estimated_effort']}
**Estimated Duration:** {task_definition.get('estimated_duration', 'TBD')}

## Description
{task_definition['description']}

## Acceptance Criteria Checklist
"""

            # Convert acceptance criteria to checklist format
            if task_definition.get('acceptance_criteria'):
                for criteria in task_definition['acceptance_criteria']:
                    content += f"- [ ] {criteria}\n"
            else:
                content += "- [ ] Define specific acceptance criteria during planning\n"

            content += "\n## Subtasks Checklist\n"

            if task_definition.get('subtasks'):
                for i, subtask in enumerate(task_definition['subtasks'], 1):
                    content += f"### {i}. {subtask.get('title', 'Subtask')}\n"
                    content += f"- [ ] {subtask.get('description', 'Complete this subtask')}\n"
                    if subtask.get('estimated_hours'):
                        content += f"  - **Estimated Time:** {subtask['estimated_hours']} hours\n"
                    content += "\n"
            else:
                content += "- [ ] Break down task into specific subtasks during planning\n"
                content += "- [ ] Estimate time for each subtask\n"
                content += "- [ ] Identify any additional requirements\n\n"

            content += "## Dependencies Checklist\n"
            if task_definition.get('dependencies'):
                for dep in task_definition['dependencies']:
                    content += f"- [ ] Ensure '{dep}' is completed\n"
                content += "- [ ] Verify all dependencies are satisfied before starting\n"
            else:
                content += "- [ ] Confirm no dependencies are required\n"
                content += "- [ ] Verify task can be started independently\n"

            content += "\n## Files and Folders Checklist\n"
            if task_definition.get('referenced_files'):
                for file_ref in task_definition['referenced_files']:
                    content += f"- [ ] Review/modify `{file_ref}`\n"
                content += "- [ ] Ensure all file changes are properly tested\n"
                content += "- [ ] Update file documentation if needed\n"
            else:
                content += "- [ ] Identify files that need to be created/modified\n"
                content += "- [ ] Plan file structure and organization\n"
                content += "- [ ] Document file purposes and relationships\n"

            content += "\n## Components Checklist\n"
            if task_definition.get('affected_components'):
                for component in task_definition['affected_components']:
                    content += f"- [ ] Update/test {component} component\n"
                content += "- [ ] Verify component integration works correctly\n"
                content += "- [ ] Update component documentation\n"
            else:
                content += "- [ ] Identify affected system components\n"
                content += "- [ ] Plan component interactions\n"
                content += "- [ ] Design component interfaces\n"

            content += f"\n## Technical Implementation Checklist\n"

            # Add technical notes as checklist items if available
            tech_notes = task_definition.get('technical_notes', '')
            if tech_notes and tech_notes != 'Implementation details to be defined.':
                # Split technical notes into actionable items
                tech_items = [item.strip() for item in tech_notes.split('.') if item.strip()]
                for item in tech_items:
                    if item:
                        content += f"- [ ] {item}\n"
            else:
                content += "- [ ] Research technical requirements and constraints\n"
                content += "- [ ] Design technical solution approach\n"
                content += "- [ ] Identify potential technical challenges\n"
                content += "- [ ] Plan implementation strategy\n"

            content += f"\n## Testing Checklist\n"

            # Add testing requirements as checklist items
            testing_req = task_definition.get('testing_requirements', '')
            if testing_req and testing_req != 'Testing approach to be defined.':
                # Split testing requirements into actionable items
                test_items = [item.strip() for item in testing_req.split('.') if item.strip()]
                for item in test_items:
                    if item:
                        content += f"- [ ] {item}\n"
            else:
                content += "- [ ] Write unit tests for new functionality\n"
                content += "- [ ] Write integration tests if applicable\n"
                content += "- [ ] Test edge cases and error conditions\n"
                content += "- [ ] Verify performance requirements are met\n"

            content += f"\n## Documentation Checklist\n"

            # Add documentation requirements as checklist items
            doc_req = task_definition.get('documentation_requirements', '')
            if doc_req and doc_req != 'Documentation needs to be defined.':
                # Split documentation requirements into actionable items
                doc_items = [item.strip() for item in doc_req.split('.') if item.strip()]
                for item in doc_items:
                    if item:
                        content += f"- [ ] {item}\n"
            else:
                content += "- [ ] Update code comments and docstrings\n"
                content += "- [ ] Update API documentation if applicable\n"
                content += "- [ ] Update user documentation if applicable\n"
                content += "- [ ] Update README or setup instructions if needed\n"

            content += "\n## Implementation Workflow Checklist\n"
            content += "- [ ] Review task requirements and dependencies\n"
            content += "- [ ] Set up development environment for this task\n"
            content += "- [ ] Create feature branch for this task\n"
            content += "- [ ] Implement core functionality\n"
            content += "- [ ] Write and run unit tests\n"
            content += "- [ ] Update documentation\n"
            content += "- [ ] Code review and refactoring\n"
            content += "- [ ] Integration testing\n"
            content += "- [ ] Merge to main branch\n"
            content += "- [ ] Mark task as complete\n\n"

            content += "## Quality Assurance Checklist\n"
            content += "- [ ] Code follows project coding standards\n"
            content += "- [ ] All tests pass successfully\n"
            content += "- [ ] No security vulnerabilities introduced\n"
            content += "- [ ] Performance impact is acceptable\n"
            content += "- [ ] Error handling is comprehensive\n"
            content += "- [ ] Code is properly documented\n"
            content += "- [ ] Changes are backward compatible (if required)\n\n"

            content += f"---\n"
            content += f"**Task ID:** {task_definition['id']}  \n"
            content += f"**Created:** {task_definition['created_at']}  \n"
            content += f"**Status:** {task_definition['status']}  \n"

            return content

        except Exception as e:
            logger.error(f"Error generating task file content: {e}")
            raise

    async def _save_task_file(
        self,
        project_id: str,
        task_definition: Dict[str, Any],
        content: str,
        collaboration_session_id: str
    ) -> str:
        """
        Save task file to database.

        Args:
            project_id: Project ID
            task_definition: Task definition
            content: Task file content
            collaboration_session_id: Associated collaboration session ID

        Returns:
            Generated file ID
        """
        try:
            file_id = str(uuid.uuid4())

            # Create file record
            file_data = GeneratedProjectFile(
                id=file_id,
                project_id=project_id,
                collaboration_session_id=collaboration_session_id,
                file_name=f"Task_{task_definition['task_number']:02d}_{task_definition['category']}.md",
                file_type="task",
                file_path=f"/tasks/Task_{task_definition['task_number']:02d}_{task_definition['category']}.md",
                content=content,
                generated_by_agents=["task_planner"],
                generation_context={
                    "task_id": task_definition["id"],
                    "task_number": task_definition["task_number"],
                    "category": task_definition["category"],
                    "priority": task_definition["priority"]
                },
                file_dependencies=self._convert_dependencies_to_file_paths(task_definition.get("dependencies", [])),
                referenced_files=self._enhance_referenced_files(task_definition.get("referenced_files", []), content),
                status="generated",
                created_at=datetime.utcnow().isoformat()
            )

            # Save to database
            file_dict = file_data.dict()
            self.generated_files_db.insert(file_dict)

            logger.info(f"Saved task file {file_id} for task {task_definition['task_number']}")
            return file_id

        except Exception as e:
            logger.error(f"Error saving task file: {e}")
            raise

    async def _generate_task_index(
        self,
        project_id: str,
        task_definitions: List[Dict[str, Any]],
        collaboration_session_id: str
    ) -> str:
        """
        Generate task index file.

        Args:
            project_id: Project ID
            task_definitions: List of task definitions
            collaboration_session_id: Associated collaboration session ID

        Returns:
            Index file ID
        """
        try:
            # Create index content
            content = f"# Project Tasks Index\n\n"
            content += f"This document provides an overview of all project tasks and their organization.\n\n"
            content += f"**Total Tasks:** {len(task_definitions)}  \n"
            content += f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  \n\n"

            # Group tasks by category
            categories = {}
            for task in task_definitions:
                category = task.get("category", "general")
                if category not in categories:
                    categories[category] = []
                categories[category].append(task)

            content += "## Tasks by Category\n\n"

            for category, tasks in categories.items():
                content += f"### {category.title()} ({len(tasks)} tasks)\n\n"

                for task in sorted(tasks, key=lambda t: t.get("task_number", 0)):
                    content += f"- **Task {task['task_number']:02d}:** [{task['title']}](./Task_{task['task_number']:02d}_{task['category']}.md)\n"
                    content += f"  - Priority: {task.get('priority', 'medium').title()}\n"
                    content += f"  - Effort: {task.get('estimated_effort', 'TBD')}\n"
                    content += f"  - Complexity: {task.get('complexity_level', 'medium').title()}\n"
                    if task.get('dependencies'):
                        content += f"  - Dependencies: {', '.join(task['dependencies'])}\n"
                    content += "\n"

            content += "## Task Dependencies\n\n"
            content += "```mermaid\n"
            content += "graph TD\n"

            # Create dependency graph
            for task in task_definitions:
                task_id = f"T{task['task_number']:02d}"
                task_title = task['title'][:30] + "..." if len(task['title']) > 30 else task['title']
                content += f"    {task_id}[\"{task_title}\"]\n"

                for dep in task.get('dependencies', []):
                    # Find dependency task number
                    dep_task = next((t for t in task_definitions if t['title'] == dep), None)
                    if dep_task:
                        dep_id = f"T{dep_task['task_number']:02d}"
                        content += f"    {dep_id} --> {task_id}\n"

            content += "```\n\n"

            content += "## Implementation Roadmap Checklist\n\n"

            # Group by priority
            high_priority = [t for t in task_definitions if t.get('priority') == 'high']
            medium_priority = [t for t in task_definitions if t.get('priority') == 'medium']
            low_priority = [t for t in task_definitions if t.get('priority') == 'low']

            content += "### Phase 1: High Priority Tasks\n"
            for task in sorted(high_priority, key=lambda t: t.get("task_number", 0)):
                content += f"- [ ] Task {task['task_number']:02d}: {task['title']}\n"

            content += "\n### Phase 2: Medium Priority Tasks\n"
            for task in sorted(medium_priority, key=lambda t: t.get("task_number", 0)):
                content += f"- [ ] Task {task['task_number']:02d}: {task['title']}\n"

            content += "\n### Phase 3: Low Priority Tasks\n"
            for task in sorted(low_priority, key=lambda t: t.get("task_number", 0)):
                content += f"- [ ] Task {task['task_number']:02d}: {task['title']}\n"

            content += "\n## Project Completion Checklist\n"
            content += "- [ ] All high priority tasks completed\n"
            content += "- [ ] All medium priority tasks completed\n"
            content += "- [ ] All low priority tasks completed\n"
            content += "- [ ] Integration testing completed\n"
            content += "- [ ] Documentation finalized\n"
            content += "- [ ] Code review completed\n"
            content += "- [ ] Performance testing completed\n"
            content += "- [ ] Security review completed\n"
            content += "- [ ] Deployment preparation completed\n"
            content += "- [ ] Project ready for release\n"

            content += "\n## Quick Reference\n\n"
            content += "| Task | Title | Category | Priority | Effort |\n"
            content += "|------|-------|----------|----------|--------|\n"

            for task in sorted(task_definitions, key=lambda t: t.get("task_number", 0)):
                content += f"| {task['task_number']:02d} | {task['title'][:40]} | {task.get('category', 'general')} | {task.get('priority', 'medium')} | {task.get('estimated_effort', 'TBD')} |\n"

            # Save index file
            file_id = str(uuid.uuid4())

            file_data = GeneratedProjectFile(
                id=file_id,
                project_id=project_id,
                collaboration_session_id=collaboration_session_id,
                file_name="TASKS_INDEX.md",
                file_type="task_index",
                file_path="/tasks/TASKS_INDEX.md",
                content=content,
                generated_by_agents=["task_planner"],
                generation_context={
                    "total_tasks": len(task_definitions),
                    "categories": list(categories.keys())
                },
                status="generated",
                created_at=datetime.utcnow().isoformat()
            )

            # Save to database
            file_dict = file_data.model_dump()
            self.generated_files_db.insert(file_dict)

            logger.info(f"Generated task index file {file_id} with {len(task_definitions)} tasks")
            return file_id

        except Exception as e:
            logger.error(f"Error generating task index: {e}")
            raise

    def _convert_dependencies_to_file_paths(self, dependencies: List[str]) -> List[str]:
        """Convert task title dependencies to file paths."""
        file_paths = []

        for dep in dependencies:
            # Convert task titles to likely file paths
            if "setup" in dep.lower() or "environment" in dep.lower():
                file_paths.extend(["package.json", "requirements.txt", "Dockerfile", ".env"])
            elif "architecture" in dep.lower() or "core" in dep.lower():
                file_paths.extend(["src/", "src/core/", "src/main.py", "src/app.py"])
            elif "database" in dep.lower():
                file_paths.extend(["src/models/", "migrations/", "database.py"])
            elif "api" in dep.lower() or "endpoint" in dep.lower():
                file_paths.extend(["src/api/", "src/routes/", "src/controllers/"])
            elif "frontend" in dep.lower() or "ui" in dep.lower():
                file_paths.extend(["src/components/", "src/pages/", "public/"])
            elif "test" in dep.lower():
                file_paths.extend(["tests/", "test/", "spec/"])
            elif "deploy" in dep.lower():
                file_paths.extend(["Dockerfile", "docker-compose.yml", "deploy/"])

        return list(set(file_paths))  # Remove duplicates

    def _enhance_referenced_files(self, base_files: List[str], content: str) -> List[str]:
        """Enhance referenced files by extracting from content."""
        import re

        enhanced_files = list(base_files)

        # Extract file references from task content
        file_patterns = [
            r'`([^`]+\.[a-zA-Z0-9]+)`',  # Files in backticks
            r'`([^`]+/[^`]*)`',          # Paths in backticks
            r'- ([^-\n]+\.[a-zA-Z0-9]+)',      # Files in lists
            r'(?:file|File):\s*([^\s\n]+\.[a-zA-Z0-9]+)',  # File: filename.ext
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                clean_match = match.strip()
                if clean_match and clean_match not in enhanced_files:
                    if not any(exclude in clean_match.lower() for exclude in ['http', 'www', 'example']):
                        enhanced_files.append(clean_match)

        return enhanced_files[:15]  # Limit to 15 most relevant files

    async def get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all tasks for a project.

        Args:
            project_id: Project ID

        Returns:
            List of task definitions
        """
        try:
            all_tasks = self.task_definitions_db.get_all()
            project_tasks = [
                task for task in all_tasks
                if task.get("project_id") == project_id
            ]

            # Sort by task number
            project_tasks.sort(key=lambda t: t.get("task_number", 0))

            return project_tasks

        except Exception as e:
            logger.error(f"Error getting project tasks: {e}")
            return []

    async def get_task_files(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all task files for a project.

        Args:
            project_id: Project ID

        Returns:
            List of task files
        """
        try:
            all_files = self.generated_files_db.get_all()
            task_files = [
                file for file in all_files
                if file.get("project_id") == project_id and file.get("file_type") in ["task", "task_index"]
            ]

            # Sort by file name
            task_files.sort(key=lambda f: f.get("file_name", ""))

            return task_files

        except Exception as e:
            logger.error(f"Error getting task files: {e}")
            return []
