"""
Project Overview Generator Service.

This service generates comprehensive ProjectOverview.md files with complete
file/folder structure, technical architecture, and project specifications
based on agent collaboration results.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.database.tinydb_handler import get_generated_files_db, get_project_structure_db
from app.models.schemas import GeneratedProjectFile, ProjectStructure, ProjectStructureNode
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class ProjectOverviewGenerator:
    """Service for generating comprehensive project overviews."""
    
    def __init__(self):
        """Initialize the project overview generator."""
        self.generated_files_db = get_generated_files_db()
        self.project_structure_db = get_project_structure_db()
        logger.info("Project Overview Generator initialized")
    
    async def generate_project_overview(
        self, 
        project_id: str, 
        collaboration_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive ProjectOverview.md based on collaboration results.
        
        Args:
            project_id: Project ID
            collaboration_results: Results from agent collaboration
            
        Returns:
            Generated project overview information
        """
        try:
            logger.info(f"Generating project overview for project {project_id}")
            
            # Extract collaboration insights
            final_consensus = collaboration_results["final_consensus"]
            
            # Generate project structure first
            project_structure = await self._generate_project_structure(
                project_id, final_consensus
            )
            
            # Generate comprehensive overview content
            overview_content = await self._generate_overview_content(
                project_id, final_consensus, project_structure
            )
            
            # Save project overview file
            overview_file_id = await self._save_project_overview_file(
                project_id, overview_content, collaboration_results["session_id"]
            )
            
            # Save project structure
            structure_id = await self._save_project_structure(
                project_id, project_structure
            )
            
            return {
                "overview_file_id": overview_file_id,
                "structure_id": structure_id,
                "project_structure": project_structure,
                "overview_content": overview_content,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate project overview: {e}")
            raise
    
    async def _generate_project_structure(
        self, 
        project_id: str, 
        final_consensus: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate detailed project file and folder structure.
        
        Args:
            project_id: Project ID
            final_consensus: Final consensus from collaboration
            
        Returns:
            Detailed project structure
        """
        try:
            logger.info(f"Generating project structure for {project_id}")
            
            # Create structure generation prompt
            structure_prompt = self._create_structure_generation_prompt(final_consensus)
            
            # Create structure generation agent if not exists
            structure_agent_id = "structure_architect"
            if structure_agent_id not in self.crew_service.agents:
                self.crew_service.create_agent(
                    name=structure_agent_id,
                    role="Project Structure Architect",
                    goal="Design comprehensive and logical project file and folder structures",
                    backstory="Expert in project organization, file structure design, and development best practices.",
                    verbose=True
                )
            
            # Create structure generation task
            structure_task = self.crew_service.create_task(
                description=structure_prompt,
                agent=self.crew_service.agents[structure_agent_id],
                expected_output="Detailed JSON structure representing the complete project file and folder hierarchy."
            )
            
            # Execute structure generation
            crew_name = f"structure_generation_{project_id}"
            crew = self.crew_service.create_crew(
                name=crew_name,
                agents=[self.crew_service.agents[structure_agent_id]],
                tasks=[structure_task],
                verbose=True
            )
            
            result = await self.crew_service.execute_crew(
                crew_name,
                inputs={
                    "project_id": project_id,
                    "consensus": final_consensus
                }
            )
            
            # Process structure result
            structure_output = result.get("result", "")
            if hasattr(structure_output, 'raw'):
                structure_output = str(structure_output.raw)
            
            # Parse structure (try JSON first, fallback to text parsing)
            project_structure = self._parse_project_structure(structure_output)
            
            logger.info(f"Generated project structure with {project_structure.get('total_files', 0)} files")
            return project_structure
            
        except Exception as e:
            logger.error(f"Error generating project structure: {e}")
            raise
    
    def _create_structure_generation_prompt(self, final_consensus: Dict[str, Any]) -> str:
        """Create prompt for project structure generation."""
        return f"""
# Project Structure Generation

Based on the following collaboration results, generate a comprehensive project file and folder structure.

## Collaboration Results
**Project Understanding:** {final_consensus.get('project_understanding', {})}
**Architecture Decisions:** {final_consensus.get('architecture', {})}
**Task Planning:** {final_consensus.get('task_planning', {})}
**Final Decisions:** {final_consensus.get('final_decisions', {})}

## Structure Requirements
1. Create a logical, scalable folder hierarchy
2. Include all necessary configuration files
3. Organize code by feature/module where appropriate
4. Include documentation, testing, and deployment folders
5. Follow industry best practices for the chosen technology stack
6. Ensure structure supports modular development

## Output Format
Provide the structure as a detailed JSON object with the following format:
```json
{{
  "name": "project-root",
  "type": "folder",
  "path": "/",
  "description": "Root project directory",
  "children": [
    {{
      "name": "src",
      "type": "folder", 
      "path": "/src",
      "description": "Source code directory",
      "children": [...]
    }},
    {{
      "name": "README.md",
      "type": "file",
      "path": "/README.md",
      "description": "Project documentation"
    }}
  ]
}}
```

## Guidelines
- Include typical files like README.md, package.json, requirements.txt, etc.
- Create logical groupings for components, services, utilities
- Include test directories alongside source code
- Add configuration directories for different environments
- Include build/deployment related files and folders
- Ensure the structure supports the planned architecture

Generate a comprehensive structure that will support scalable, modular application development.
"""
    
    async def _generate_overview_content(
        self,
        project_id: str,
        final_consensus: Dict[str, Any],
        project_structure: Dict[str, Any]
    ) -> str:
        """
        Generate comprehensive ProjectOverview.md content.

        Args:
            project_id: Project ID
            final_consensus: Final consensus from collaboration
            project_structure: Generated project structure

        Returns:
            Complete ProjectOverview.md content
        """
        try:
            logger.info(f"Generating overview content for {project_id}")
            logger.info(f"Final consensus data: {str(final_consensus)[:200]}...")
            logger.info(f"Project structure data: {str(project_structure)[:200]}...")

            # Create overview generation prompt
            overview_prompt = self._create_overview_generation_prompt(
                final_consensus, project_structure
            )

            # Create overview generation agent if not exists
            overview_agent_id = "overview_writer"
            if overview_agent_id not in self.crew_service.agents:
                self.crew_service.create_agent(
                    name=overview_agent_id,
                    role="Technical Documentation Specialist",
                    goal="Create comprehensive and clear project documentation",
                    backstory="Expert in technical writing, project documentation, and creating clear specifications.",
                    verbose=True
                )

            # Create overview generation task
            overview_task = self.crew_service.create_task(
                description=overview_prompt,
                agent=self.crew_service.agents[overview_agent_id],
                expected_output="Complete ProjectOverview.md content in markdown format with all required sections."
            )

            # Execute overview generation
            crew_name = f"overview_generation_{project_id}"
            crew = self.crew_service.create_crew(
                name=crew_name,
                agents=[self.crew_service.agents[overview_agent_id]],
                tasks=[overview_task],
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

            # Process overview result
            overview_content = result.get("result", "")
            if hasattr(overview_content, 'raw'):
                overview_content = str(overview_content.raw)

            logger.info(f"Raw overview content from CrewAI: {str(overview_content)[:200]}...")

            # Check if content is substantial
            if not overview_content or len(overview_content.strip()) < 100:
                logger.warning("CrewAI generated insufficient content, using fallback")
                overview_content = self._generate_overview_fallback(final_consensus, project_structure)

            # Ensure content is properly formatted
            if not overview_content.startswith("# "):
                overview_content = f"# Project Overview\n\n{overview_content}"

            logger.info(f"Final overview content ({len(overview_content)} characters)")
            return overview_content

        except Exception as e:
            logger.error(f"Error generating overview content: {e}")
            logger.info("Using fallback overview generation")
            return self._generate_overview_fallback(final_consensus, project_structure)
    
    def _create_overview_generation_prompt(
        self, 
        final_consensus: Dict[str, Any], 
        project_structure: Dict[str, Any]
    ) -> str:
        """Create prompt for overview content generation."""
        return f"""
# ProjectOverview.md Generation

Create a comprehensive ProjectOverview.md document based on the collaboration results and project structure.

## Collaboration Results
{final_consensus}

## Project Structure
{project_structure}

## Required Sections
1. **Project Description** - Clear overview of what the project does
2. **Objectives and Goals** - What the project aims to achieve
3. **Technical Architecture** - High-level system design and architecture
4. **Technology Stack** - Technologies, frameworks, and tools used
5. **Project Structure** - Detailed file and folder organization
6. **Key Components** - Main modules and their responsibilities
7. **Data Flow** - How data moves through the system
8. **API Design** - API endpoints and interfaces (if applicable)
9. **Database Schema** - Data models and relationships (if applicable)
10. **Security Considerations** - Security measures and best practices
11. **Performance Requirements** - Performance goals and optimizations
12. **Deployment Strategy** - How the application will be deployed
13. **Development Workflow** - Development process and guidelines
14. **Testing Strategy** - Testing approach and requirements
15. **Documentation Plan** - Documentation requirements and structure
16. **Implementation Roadmap** - High-level development phases
17. **Deliverables** - Expected project outputs and milestones

## Content Guidelines
- Use clear, professional markdown formatting
- Include code examples where relevant
- Add diagrams descriptions (actual diagrams will be added later)
- Be specific and actionable
- Reference the project structure files and folders
- Include technical specifications and requirements
- Ensure content supports scalable, modular development

## Output Format
Provide complete markdown content that can be saved directly as ProjectOverview.md.
Include proper headings, lists, code blocks, and formatting.

Generate comprehensive documentation that will serve as the definitive project specification.
"""

    def _generate_overview_fallback(
        self,
        final_consensus: Dict[str, Any],
        project_structure: Dict[str, Any]
    ) -> str:
        """Generate fallback overview content when CrewAI fails."""
        try:
            logger.info(f"Generating fallback overview content")
            logger.info(f"Final consensus keys: {list(final_consensus.keys())}")

            # Extract project information from consensus - try multiple possible locations
            project_info = final_consensus.get("project_context", {})
            logger.info(f"Project context found: {bool(project_info)}")

            # If project_context is empty, try to get from the consensus directly
            if not project_info:
                logger.info("No project_context found, trying consensus directly")
                project_info = final_consensus

            # Also try to get from project_data if available
            if "project_data" in final_consensus:
                logger.info("Found project_data in consensus, merging")
                project_data = final_consensus["project_data"]
                project_info.update(project_data)

            logger.info(f"Final project_info keys: {list(project_info.keys())}")

            # Extract project details with comprehensive fallbacks
            project_name = project_info.get("name", "Project")
            project_description = project_info.get("description", "A comprehensive software project")
            requirements = project_info.get("requirements", "")
            tech_stack = project_info.get("tech_stack", [])
            estimated_timeline = project_info.get("estimated_timeline", "")
            team_size = project_info.get("team_size", "")
            budget_constraints = project_info.get("budget_constraints", "")
            priority_level = project_info.get("priority_level", "")
            tags = project_info.get("tags", [])

            # Build comprehensive overview using actual project details
            overview_content = f"""# {project_name}

## Project Description
{project_description if project_description else "A comprehensive software project designed to meet specific requirements and deliver value to users."}

## Requirements
{requirements if requirements else "Requirements to be defined based on project scope and objectives."}

## Technical Architecture
The project follows modern software development practices with a focus on modular architecture, scalable design patterns, security best practices, and performance optimization.

## Technology Stack
"""

            if tech_stack:
                for tech in tech_stack:
                    overview_content += f"- {tech}\n"
            else:
                overview_content += "- Modern web technologies\n- Cloud-based infrastructure\n- Industry-standard frameworks\n"

            overview_content += f"""
## Project Management

### Timeline
{estimated_timeline if estimated_timeline else "Project timeline to be established based on scope and resource availability."}

### Team Structure
{team_size if team_size else "Team structure and roles to be defined based on project requirements and organizational capacity."}

### Budget Considerations
{budget_constraints if budget_constraints else "Budget considerations to be evaluated based on project scope and resource requirements."}

### Priority Level
{priority_level if priority_level else "Project priority to be established within organizational context."}

## Project Tags
{', '.join(tags) if tags else 'Project categorization tags to be assigned.'}

## Project Structure
The project is organized with a clear separation of concerns:
- Source code in dedicated directories
- Configuration files properly organized
- Documentation and testing infrastructure
- Build and deployment scripts

## Key Components
- **Core Application**: Main business logic and functionality
- **User Interface**: Frontend components and user experience
- **Data Layer**: Database models and data access patterns
- **API Layer**: RESTful services and endpoints
- **Authentication**: User management and security
- **Testing**: Comprehensive test suite

## Development Workflow
1. **Planning**: Requirements analysis and design
2. **Development**: Iterative development with regular reviews
3. **Testing**: Automated and manual testing procedures
4. **Deployment**: Continuous integration and deployment
5. **Monitoring**: Performance and error monitoring

## Implementation Roadmap
### Phase 1: Foundation
- Project setup and configuration
- Core architecture implementation
- Basic functionality development

### Phase 2: Core Features
- Main feature implementation
- User interface development
- Integration testing

### Phase 3: Enhancement
- Performance optimization
- Security hardening
- Documentation completion

## Deliverables
- Fully functional application
- Comprehensive documentation
- Test suite with good coverage
- Deployment scripts and configuration
- User guides and technical documentation

---
*Generated using fallback method with project-specific details*
"""

            return overview_content

        except Exception as e:
            logger.error(f"Error in fallback overview generation: {e}")
            return f"""# Project Overview

## Description
This is a comprehensive software project designed to meet specific requirements and deliver value to users.

## Technical Implementation
The project follows modern development practices and uses industry-standard technologies.

## Development Approach
- Agile development methodology
- Test-driven development
- Continuous integration and deployment
- Regular code reviews and quality assurance

---
*Minimal fallback content generated due to system issues*
"""

    def _parse_project_structure(self, structure_output: str) -> Dict[str, Any]:
        """Parse project structure from agent output."""
        try:
            import json
            import re
            
            # Try to extract JSON from the output
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', structure_output, re.DOTALL)
            if json_match:
                structure_json = json_match.group(1)
                structure = json.loads(structure_json)
            else:
                # Try to parse the entire output as JSON
                structure = json.loads(structure_output)
            
            # Count files and folders
            total_files, total_folders = self._count_structure_items(structure)
            
            return {
                "root_structure": structure,
                "total_files": total_files,
                "total_folders": total_folders,
                "structure_metadata": {
                    "generated_by": "structure_architect",
                    "generation_method": "ai_collaboration"
                }
            }
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse structure as JSON, creating fallback structure")
            return self._create_fallback_structure(structure_output)
    
    def _count_structure_items(self, structure: Dict[str, Any]) -> tuple:
        """Count total files and folders in structure."""
        files = 0
        folders = 0
        
        def count_recursive(node):
            nonlocal files, folders
            if node.get("type") == "file":
                files += 1
            elif node.get("type") == "folder":
                folders += 1
            
            for child in node.get("children", []):
                count_recursive(child)
        
        count_recursive(structure)
        return files, folders
    
    def _create_fallback_structure(self, structure_output: str) -> Dict[str, Any]:
        """Create fallback structure if parsing fails."""
        return {
            "root_structure": {
                "name": "project-root",
                "type": "folder",
                "path": "/",
                "description": "Root project directory",
                "children": [
                    {
                        "name": "src",
                        "type": "folder",
                        "path": "/src",
                        "description": "Source code directory",
                        "children": []
                    },
                    {
                        "name": "README.md",
                        "type": "file",
                        "path": "/README.md",
                        "description": "Project documentation"
                    }
                ]
            },
            "total_files": 1,
            "total_folders": 2,
            "structure_metadata": {
                "generated_by": "fallback",
                "original_output": structure_output[:500]  # Store first 500 chars for debugging
            }
        }

    async def _save_project_overview_file(
        self,
        project_id: str,
        content: str,
        collaboration_session_id: str
    ) -> str:
        """
        Save project overview file to database.

        Args:
            project_id: Project ID
            content: Overview content
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
                file_name="ProjectOverview.md",
                file_type="project_overview",
                file_path="/ProjectOverview.md",
                content=content,
                generated_by_agents=["overview_writer", "structure_architect"],
                generation_context={
                    "generation_type": "comprehensive_overview",
                    "includes_structure": True,
                    "includes_architecture": True
                },
                file_dependencies=[],  # Project overview typically has no dependencies
                referenced_files=self._extract_referenced_files_from_content(content),
                status="generated",
                created_at=datetime.utcnow().isoformat()
            )

            # Save to database
            file_dict = file_data.model_dump()
            self.generated_files_db.insert(file_dict)

            logger.info(f"Saved project overview file {file_id} for project {project_id}")
            return file_id

        except Exception as e:
            logger.error(f"Error saving project overview file: {e}")
            raise

    async def _save_project_structure(
        self,
        project_id: str,
        structure_data: Dict[str, Any]
    ) -> str:
        """
        Save project structure to database.

        Args:
            project_id: Project ID
            structure_data: Project structure data

        Returns:
            Structure record ID
        """
        try:
            # Create structure record
            structure = ProjectStructure(
                project_id=project_id,
                root_structure=ProjectStructureNode(**structure_data["root_structure"]),
                total_files=structure_data["total_files"],
                total_folders=structure_data["total_folders"],
                structure_metadata=structure_data["structure_metadata"],
                generated_at=datetime.utcnow().isoformat()
            )

            # Save to database
            structure_dict = structure.model_dump()
            structure_dict["id"] = str(uuid.uuid4())  # Add ID for database
            self.project_structure_db.insert(structure_dict)

            logger.info(f"Saved project structure for project {project_id}")
            return structure_dict["id"]

        except Exception as e:
            logger.error(f"Error saving project structure: {e}")
            raise

    async def get_project_overview(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project overview file for a project.

        Args:
            project_id: Project ID

        Returns:
            Project overview file data or None
        """
        try:
            # Query for project overview files
            all_files = self.generated_files_db.get_all()
            overview_files = [
                file for file in all_files
                if file.get("project_id") == project_id and file.get("file_type") == "project_overview"
            ]

            if not overview_files:
                return None

            # Return the most recent overview file
            latest_file = max(overview_files, key=lambda f: f.get("created_at", ""))
            return latest_file

        except Exception as e:
            logger.error(f"Error getting project overview: {e}")
            return None

    async def get_project_structure(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project structure for a project.

        Args:
            project_id: Project ID

        Returns:
            Project structure data or None
        """
        try:
            # Query for project structure
            all_structures = self.project_structure_db.get_all()
            project_structures = [
                structure for structure in all_structures
                if structure.get("project_id") == project_id
            ]

            if not project_structures:
                return None

            # Return the most recent structure
            latest_structure = max(project_structures, key=lambda s: s.get("generated_at", ""))
            return latest_structure

        except Exception as e:
            logger.error(f"Error getting project structure: {e}")
            return None

    async def update_project_overview(
        self,
        project_id: str,
        updated_content: str,
        update_reason: str = "Manual update"
    ) -> str:
        """
        Update project overview with new content.

        Args:
            project_id: Project ID
            updated_content: New overview content
            update_reason: Reason for update

        Returns:
            Updated file ID
        """
        try:
            # Get current overview
            current_overview = await self.get_project_overview(project_id)

            if current_overview:
                # Update existing file
                current_overview["content"] = updated_content
                current_overview["updated_at"] = datetime.utcnow().isoformat()
                current_overview["version"] = current_overview.get("version", 1) + 1

                # Add update metadata
                if "generation_context" not in current_overview:
                    current_overview["generation_context"] = {}
                current_overview["generation_context"]["last_update_reason"] = update_reason

                # Update in database
                self.generated_files_db.update_by_id(current_overview["id"], current_overview)

                logger.info(f"Updated project overview for project {project_id}")
                return current_overview["id"]
            else:
                # Create new overview file
                return await self._save_project_overview_file(
                    project_id, updated_content, "manual_update"
                )

        except Exception as e:
            logger.error(f"Error updating project overview: {e}")
            raise

    async def validate_project_structure(self, structure_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate project structure for completeness and best practices.

        Args:
            structure_data: Project structure to validate

        Returns:
            Validation results
        """
        try:
            validation_results = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "suggestions": [],
                "completeness_score": 0
            }

            root_structure = structure_data.get("root_structure", {})

            # Check for essential files
            essential_files = ["README.md", "package.json", "requirements.txt", ".gitignore"]
            found_files = self._find_files_in_structure(root_structure, essential_files)

            for file in essential_files:
                if file not in found_files:
                    validation_results["warnings"].append(f"Missing essential file: {file}")

            # Check for logical folder structure
            expected_folders = ["src", "tests", "docs", "config"]
            found_folders = self._find_folders_in_structure(root_structure, expected_folders)

            for folder in expected_folders:
                if folder not in found_folders:
                    validation_results["suggestions"].append(f"Consider adding folder: {folder}")

            # Calculate completeness score
            total_checks = len(essential_files) + len(expected_folders)
            passed_checks = len(found_files) + len(found_folders)
            validation_results["completeness_score"] = (passed_checks / total_checks) * 100

            return validation_results

        except Exception as e:
            logger.error(f"Error validating project structure: {e}")
            return {
                "is_valid": False,
                "errors": [str(e)],
                "warnings": [],
                "suggestions": [],
                "completeness_score": 0
            }

    def _find_files_in_structure(self, structure: Dict[str, Any], target_files: List[str]) -> List[str]:
        """Find specific files in project structure."""
        found_files = []

        def search_recursive(node):
            if node.get("type") == "file" and node.get("name") in target_files:
                found_files.append(node.get("name"))

            for child in node.get("children", []):
                search_recursive(child)

        search_recursive(structure)
        return found_files

    def _find_folders_in_structure(self, structure: Dict[str, Any], target_folders: List[str]) -> List[str]:
        """Find specific folders in project structure."""
        found_folders = []

        def search_recursive(node):
            if node.get("type") == "folder" and node.get("name") in target_folders:
                found_folders.append(node.get("name"))

            for child in node.get("children", []):
                search_recursive(child)

        search_recursive(structure)
        return found_folders

    def _extract_referenced_files_from_content(self, content: str) -> List[str]:
        """Extract file references from markdown content."""
        import re

        referenced_files = []

        # Common file patterns to look for in content
        file_patterns = [
            r'`([^`]+\.[a-zA-Z0-9]+)`',  # Files in backticks like `package.json`
            r'`([^`]+/[^`]*)`',          # Paths in backticks like `src/main.py`
            r'\*\*([^*]+\.[a-zA-Z0-9]+)\*\*',  # Files in bold like **README.md**
            r'- ([^-\n]+\.[a-zA-Z0-9]+)',      # Files in lists like - package.json
            r'(?:file|File):\s*([^\s\n]+\.[a-zA-Z0-9]+)',  # File: filename.ext
            r'(?:path|Path):\s*([^\s\n]+)',    # Path: /some/path
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Clean up the match
                clean_match = match.strip()
                if clean_match and clean_match not in referenced_files:
                    # Filter out common false positives
                    if not any(exclude in clean_match.lower() for exclude in ['http', 'www', 'example', 'placeholder']):
                        referenced_files.append(clean_match)

        return referenced_files[:20]  # Limit to 20 most relevant files
