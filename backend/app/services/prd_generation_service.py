"""
PRD Generation Service

This service generates Product Requirements Document (PRD) content from existing project data
stored in the database, eliminating the need for users to manually input project details.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.database.tinydb_handler import get_projects_db, get_project_files_db

logger = logging.getLogger(__name__)


class PRDGenerationService:
    """Service for generating PRD content from project data."""
    
    def __init__(self):
        self.projects_db = get_projects_db()
        self.project_files_db = get_project_files_db()
    
    def generate_prd_from_project(self, project_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive PRD from existing project data.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with PRD content and metadata
        """
        try:
            # Get project from database
            project = self.projects_db.get_by_id(project_id)
            if not project:
                return {
                    "success": False,
                    "error": "Project not found",
                    "prd_content": ""
                }
            
            # Check if there's an existing project overview file
            existing_overview = self._get_existing_project_overview(project_id)
            
            # Generate PRD content
            prd_content = self._build_prd_content(project, existing_overview)
            
            return {
                "success": True,
                "prd_content": prd_content,
                "project_name": project.get("name", "Untitled Project"),
                "has_existing_overview": existing_overview is not None,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating PRD for project {project_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "prd_content": ""
            }
    
    def _get_existing_project_overview(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get existing project overview file if it exists."""
        try:
            all_files = self.project_files_db.get_all()
            overview_files = [
                file for file in all_files 
                if (file.get("project_id") == project_id and 
                    file.get("file_type") == "project_overview" and
                    file.get("metadata", {}).get("is_primary", False))
            ]
            
            # Return the most recent overview file
            if overview_files:
                return max(overview_files, key=lambda x: x.get("created_at", ""))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting existing project overview: {str(e)}")
            return None
    
    def _build_prd_content(self, project: Dict[str, Any], existing_overview: Optional[Dict[str, Any]] = None) -> str:
        """Build comprehensive PRD content from project data."""
        
        # Start with project header
        project_name = project.get("name", "Untitled Project")
        prd_content = f"""# Product Requirements Document (PRD)
## {project_name}

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Project ID:** {project.get("id", "N/A")}
**Status:** {project.get("status", "draft").title()}

---

"""
        
        # Project Overview Section
        prd_content += "## 1. Project Overview\n\n"

        description = project.get("description", "")
        if description:
            prd_content += f"### Description\n{description}\n\n"

        # Requirements Section
        prd_content += "## 2. Requirements\n\n"

        requirements = project.get("requirements", "")
        if requirements:
            prd_content += f"### Functional Requirements\n{requirements}\n\n"

        # Technical Specifications
        prd_content += "## 3. Technical Specifications\n\n"

        tech_stack = project.get("tech_stack", [])
        if tech_stack:
            prd_content += "### Technology Stack\n"
            for tech in tech_stack:
                prd_content += f"- {tech}\n"
            prd_content += "\n"
        
        scalability_requirements = project.get("scalability_requirements", "")
        if scalability_requirements:
            prd_content += f"### Scalability Requirements\n{scalability_requirements}\n\n"
        
        performance_requirements = project.get("performance_requirements", "")
        if performance_requirements:
            prd_content += f"### Performance Requirements\n{performance_requirements}\n\n"
        
        security_requirements = project.get("security_requirements", "")
        if security_requirements:
            prd_content += f"### Security Requirements\n{security_requirements}\n\n"
        
        integration_requirements = project.get("integration_requirements", "")
        if integration_requirements:
            prd_content += f"### Integration Requirements\n{integration_requirements}\n\n"
        
        # Constraints and Considerations
        prd_content += "## 4. Constraints and Considerations\n\n"
        
        constraints = project.get("constraints", "")
        if constraints:
            prd_content += f"### Project Constraints\n{constraints}\n\n"
        
        estimated_timeline = project.get("estimated_timeline", "")
        if estimated_timeline:
            prd_content += f"### Timeline\n{estimated_timeline}\n\n"
        
        team_size = project.get("team_size", "")
        if team_size:
            prd_content += f"### Team Size\n{team_size}\n\n"
        
        budget_constraints = project.get("budget_constraints", "")
        if budget_constraints:
            prd_content += f"### Budget Constraints\n{budget_constraints}\n\n"
        
        priority_level = project.get("priority_level", "")
        if priority_level:
            prd_content += f"### Priority Level\n{priority_level}\n\n"
        
        # Project Tags
        tags = project.get("tags", [])
        if tags:
            prd_content += "## 5. Project Tags\n\n"
            prd_content += f"**Tags:** {', '.join(tags)}\n\n"
        
        # Existing Overview Integration
        if existing_overview:
            prd_content += "## 6. Existing Project Overview\n\n"
            prd_content += "### Previous Analysis\n"
            prd_content += f"*Generated on: {existing_overview.get('created_at', 'Unknown')}*\n\n"
            
            overview_content = existing_overview.get("content", "")
            if overview_content:
                # Extract relevant sections from existing overview
                prd_content += f"{overview_content}\n\n"
        
        # Additional Context
        metadata = project.get("metadata", {})
        if metadata:
            prd_content += "## 7. Additional Context\n\n"
            for key, value in metadata.items():
                if value and str(value).strip():
                    formatted_key = key.replace("_", " ").title()
                    prd_content += f"**{formatted_key}:** {value}\n\n"
        
        # Task Generation Instructions
        prd_content += """## 8. Task Generation Instructions

Based on the above requirements and specifications, please generate detailed, actionable tasks that will help implement this project. Consider the following when creating tasks:

1. **Break down complex features** into manageable, atomic tasks
2. **Include dependencies** between tasks where applicable
3. **Consider the technology stack** and architecture preferences
4. **Account for testing and quality assurance** requirements
5. **Include documentation and deployment** tasks
6. **Prioritize tasks** based on project objectives and constraints
7. **Ensure tasks are specific and measurable** with clear acceptance criteria

The generated tasks should provide a comprehensive roadmap for implementing this project from start to finish.
"""
        
        return prd_content
    
    def get_prd_suggestions(self, project_id: str) -> Dict[str, Any]:
        """Get suggestions for improving PRD content."""
        try:
            project = self.projects_db.get_by_id(project_id)
            if not project:
                return {"success": False, "error": "Project not found"}
            
            suggestions = []
            
            # Check for missing critical information
            if not project.get("description") or len(project.get("description", "")) < 50:
                suggestions.append("Consider adding a more detailed project description")
            
            if not project.get("requirements") or len(project.get("requirements", "")) < 50:
                suggestions.append("Add more specific functional requirements")
            
            if not project.get("tech_stack") or len(project.get("tech_stack", [])) == 0:
                suggestions.append("Specify the technology stack to be used")
            
            if not project.get("estimated_timeline"):
                suggestions.append("Include estimated timeline for better task planning")
            
            return {
                "success": True,
                "suggestions": suggestions,
                "completeness_score": self._calculate_completeness_score(project)
            }
            
        except Exception as e:
            logger.error(f"Error getting PRD suggestions: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _calculate_completeness_score(self, project: Dict[str, Any]) -> int:
        """Calculate a completeness score for the project data (0-100)."""
        score = 0

        # Essential fields (higher weight)
        if project.get("name"): score += 20
        if project.get("description") and len(project.get("description", "")) >= 50: score += 30
        if project.get("requirements") and len(project.get("requirements", "")) >= 50: score += 30

        # Important fields (medium weight)
        if project.get("tech_stack") and len(project.get("tech_stack", [])) > 0: score += 10

        # Nice-to-have fields (lower weight)
        if project.get("estimated_timeline"): score += 5
        if project.get("priority_level"): score += 5

        return min(score, 100)


# Global instance
prd_generation_service = PRDGenerationService()
