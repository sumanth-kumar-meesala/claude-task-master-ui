"""
API endpoints for agent chat functionality.
"""

import logging
import uuid
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.gemini_service import get_gemini_service


from app.models.responses import SuccessResponse, ErrorResponse, ResponseStatus

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["Chat"])

# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model."""
    id: str
    type: str = Field(..., description="Message type: user, agent, system")
    content: str
    timestamp: str
    agentId: Optional[str] = None
    agentName: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatSession(BaseModel):
    """Chat session model."""
    id: str
    projectId: str
    title: str
    messages: List[ChatMessage]
    participants: List[str]  # Agent IDs
    created_at: str
    updated_at: str
    status: str = "active"

class CreateSessionRequest(BaseModel):
    """Request to create a new chat session."""
    project_id: str
    participants: List[str]
    title: Optional[str] = None

class SendMessageRequest(BaseModel):
    """Request to send a message."""
    sessionId: Optional[str] = None
    message: str
    agentId: str  # 'all' for crew, specific ID for individual agent
    context: Optional[Dict[str, Any]] = None




# Message Endpoints
@router.post("/messages", response_model=SuccessResponse)
async def send_message(request: SendMessageRequest, background_tasks: BackgroundTasks):
    """Send a message and get agent response."""
    try:

        # Generate a simple session ID for this conversation
        session_id = request.sessionId or str(uuid.uuid4())

        # Add user message
        user_message = {
            "id": str(uuid.uuid4()),
            "type": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Execute Gemini chat
        result = await execute_gemini_chat(request)
        agent_name = "AI Assistant"
        agent_icon = "assistant"

        # Add agent response
        agent_message = {
            "id": str(uuid.uuid4()),
            "type": "agent",
            "content": result.get("result", result.get("output", "No response")),
            "timestamp": datetime.utcnow().isoformat(),
            "agentId": request.agentId,
            "agentName": agent_name,
            "metadata": {
                "execution_time": result.get("execution_time", 0),
                "agent_icon": agent_icon
            }
        }

        return SuccessResponse(
            data={
                "message": agent_message,
                "session": {
                    "id": session_id,
                    "messages": [user_message, agent_message]
                }
            },
            message="Message sent successfully"
        )

    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

# Simple Gemini-based chat helper
async def execute_gemini_chat(request: SendMessageRequest):
    """Execute chat using Gemini API directly."""
    try:
        from app.services.gemini_service import get_gemini_service

        gemini_service = get_gemini_service()

        # Create a simple prompt for project assistance
        prompt = f"""You are a helpful AI assistant for project planning and development.
        Please provide a helpful response to the following message:

        {request.message}

        Provide practical, actionable advice for project development and planning."""

        response = await gemini_service.generate_response(prompt)

        return {
            "result": response,
            "output": response,
            "execution_time": 1.0,
            "model": "gemini"
        }

    except Exception as e:
        logger.error(f"Failed to execute Gemini chat: {e}")
        return {
            "result": f"I apologize, but I'm having trouble processing your request right now. Please try again later.",
            "output": f"Error: {str(e)}",
            "execution_time": 0,
            "model": "gemini"
        }



# Project Overview Endpoints
class ProjectOverviewRequest(BaseModel):
    """Request to save project overview."""
    project_id: str
    overview_data: Dict[str, Any]

class GenerateFilesRequest(BaseModel):
    """Request to generate project files."""
    project_id: Optional[str] = None
    project_name: str
    project_description: Optional[str] = None
    requirements: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    agents: List[str]

@router.post("/overview/save", response_model=SuccessResponse)
async def save_project_overview(request: ProjectOverviewRequest):
    """Save generated project overview."""
    try:
        # For now, just return success without saving to sessions
        # This can be enhanced to save to project files or another storage mechanism
        overview_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        overview_data = {
            "id": overview_id,
            "project_id": request.project_id,
            "overview_data": request.overview_data,
            "created_at": now,
            "updated_at": now
        }

        return SuccessResponse(
            message="Project overview saved successfully",
            data=overview_data
        )

    except Exception as e:
        logger.error(f"Failed to save project overview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save overview: {str(e)}")

@router.get("/overview/{project_id}", response_model=SuccessResponse)
async def get_project_overview(project_id: str):
    """Get project overview by project ID."""
    try:
        # For now, return a not found response since we're not storing overviews
        # This can be enhanced to retrieve from project files or another storage mechanism
        raise HTTPException(status_code=404, detail="Project overview not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project overview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get overview: {str(e)}")


@router.post("/generate-files", response_model=SuccessResponse)
async def generate_project_files(request: GenerateFilesRequest):
    """Generate project documentation files based on conversation."""
    try:
        crew_service = get_crew_service()
        sessions_db = get_sessions_db()

        # Create comprehensive context for generation
        generation_context = {
            "project_id": request.project_id,
            "project_name": request.project_name,
            "project_description": request.project_description,
            "requirements": request.requirements,
            "tech_stack": request.tech_stack,
            "conversation_history": request.conversation_history or []
        }

        # Create agents for file generation
        agents = []
        for agent_id in request.agents:
            agent = crew_service.get_agent(agent_id)
            if not agent:
                # Create specialized generation agent
                agent = crew_service.create_agent(
                    name=f"file_generator_{agent_id}",
                    role=f"Project Documentation Specialist",
                    goal="Generate comprehensive project documentation based on conversation context",
                    backstory=f"You are an expert at creating detailed project documentation including overviews, technical specifications, and task breakdowns. You analyze conversations and project context to create accurate, actionable documentation."
                )
            agents.append(agent)

        # Create tasks for file generation
        tasks = []

        # Task 1: Generate ProjectOverview.md
        overview_task = crew_service.create_task(
            description=f"""
            Based on the project context and conversation history, generate a comprehensive ProjectOverview.md file with the following sections:

            # {request.project_name} - Project Overview

            ## Executive Summary
            - High-level project overview and business value
            - Key objectives and goals

            ## Technical Architecture
            - System design and technology stack
            - Architecture patterns and decisions

            ## Implementation Plan
            - Detailed project phases and milestones
            - Development approach and methodology

            ## Risk Assessment
            - Potential risks and mitigation strategies
            - Technical and business risks

            ## Resource Requirements
            - Team composition and skills needed
            - Infrastructure and tool requirements

            ## Timeline Estimate
            - Realistic timeline estimates for project phases
            - Key milestones and deliverables

            ## Success Metrics
            - Key performance indicators
            - Definition of done criteria

            Project Context:
            - Name: {request.project_name}
            - Description: {request.project_description or 'Not provided'}
            - Requirements: {request.requirements or 'Not provided'}
            - Tech Stack: {', '.join(request.tech_stack) if request.tech_stack else 'Not specified'}

            Use the conversation history to understand the project requirements and create detailed, actionable documentation.
            """,
            agent=agents[0],
            expected_output="Complete ProjectOverview.md file content in markdown format"
        )
        tasks.append(overview_task)

        # Task 2: Generate Tasks files
        tasks_task = crew_service.create_task(
            description=f"""
            Based on the project context and conversation history, generate detailed task breakdown files:

            Create multiple Tasks(N).md files where N is the task number, with the following structure for each:

            # Task N: [Task Title]

            ## Description
            Detailed description of what needs to be accomplished

            ## Acceptance Criteria
            - Specific, measurable criteria for completion
            - Clear definition of done

            ## Technical Requirements
            - Technical specifications and constraints
            - Dependencies and prerequisites

            ## Implementation Steps
            1. Step-by-step breakdown of implementation
            2. Detailed technical approach
            3. Testing and validation steps

            ## Estimated Effort
            - Time estimate for completion
            - Complexity assessment

            ## Dependencies
            - Other tasks or external dependencies
            - Blocking or prerequisite items

            Break down the project into logical, manageable tasks covering:
            - Setup and infrastructure
            - Core functionality development
            - Testing and quality assurance
            - Documentation and deployment

            Generate at least 5-10 detailed task files based on the project scope and requirements.
            """,
            agent=agents[-1] if len(agents) > 1 else agents[0],
            expected_output="Multiple Tasks(N).md files with detailed task breakdowns"
        )
        tasks.append(tasks_task)

        # Create and execute crew
        crew_name = f"file_generation_{request.project_id}_{int(datetime.utcnow().timestamp())}"
        crew = crew_service.create_crew(
            name=crew_name,
            agents=agents,
            tasks=tasks
        )

        # Execute crew
        crew_result = await crew_service.execute_crew(crew_name, generation_context)

        # Return generation results without saving to sessions
        generation_id = str(uuid.uuid4())

        return SuccessResponse(
            message="Project files generated successfully",
            data={
                "generation_id": generation_id,
                "files_generated": ["ProjectOverview.md", "Tasks(1-N).md"],
                "result": crew_result.get("result", "Files generated"),
                "execution_time": crew_result.get("duration", 0),
                "project_name": request.project_name,
                "agents_used": request.agents
            }
        )

    except Exception as e:
        logger.error(f"Failed to generate project files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate files: {str(e)}")











@router.get("/overviews", response_model=SuccessResponse)
async def get_all_project_overviews():
    """Get all project overviews."""
    try:
        # Return empty list since we're not storing overviews in sessions anymore
        return SuccessResponse(
            message="Project overviews retrieved successfully",
            data={"overviews": []}
        )

    except Exception as e:
        logger.error(f"Failed to get project overviews: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get overviews: {str(e)}")
















# File generation functions
async def generate_project_files_from_orchestration(
    project_context: Dict[str, Any],
    agent_outputs: Dict[str, Any],
    agents_used: List[str]
) -> List[str]:
    """Generate project files from orchestration results and save to database."""
    try:
        from app.services.file_storage_service import get_file_storage_service

        project_id = project_context.get("project_id")
        if not project_id:
            logger.error("No project_id provided in project_context")
            return []

        logger.info(f"Generating project files for project {project_id}")

        file_storage_service = get_file_storage_service()

        # Generate and save project overview
        logger.info("Generating ProjectOverview.md content...")
        overview_content = generate_project_overview_content(project_context, agent_outputs)

        if not overview_content or len(overview_content.strip()) < 100:
            # Generate fallback content if content is too short
            project_name = project_context.get("project_name", "Untitled Project")
            overview_content = f"""# {project_name} - Project Overview

## Project Information
- **Name**: {project_name}
- **Description**: {project_context.get('project_description', 'No description provided')}
- **Technology Stack**: {', '.join(project_context.get('tech_stack', [])) if project_context.get('tech_stack') else 'Not specified'}
- **Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Executive Summary
This project overview was generated through automated analysis. The project requires comprehensive planning and implementation using modern development practices.

## Requirements
{project_context.get('requirements', 'No specific requirements provided')}

## Agent Analysis
The following agents participated in the analysis:
{chr(10).join([f"- {agent}" for agent in agents_used])}

## Next Steps
1. Review and refine project requirements
2. Develop detailed technical specifications
3. Create implementation timeline
4. Begin development phase
"""

        # Save project overview to database
        overview_file_id = await file_storage_service.save_project_overview(
            project_id=project_id,
            content=overview_content,
            agents_used=agents_used,
            generation_context=project_context
        )

        logger.info(f"ProjectOverview.md saved to database with ID: {overview_file_id}")

        # Generate and save task files
        logger.info("Generating task files...")
        task_definitions = generate_comprehensive_tasks(project_context, agent_outputs)

        # Prepare task files data
        task_files_data = []

        # Generate individual task files
        for i, task_def in enumerate(task_definitions, 1):
            task_content = f"""# Task {i}: {task_def['title']}

## Description
{task_def['description']}

## Acceptance Criteria
{chr(10).join([f"- {criteria}" for criteria in task_def['acceptance_criteria']])}

## Technical Requirements
{chr(10).join([f"- {req}" for req in task_def['technical_requirements']])}

## Implementation Steps
{chr(10).join([f"{j}. {step}" for j, step in enumerate(task_def['implementation_steps'], 1)])}

## Subtasks
{chr(10).join([f"- [ ] {subtask}" for subtask in task_def['subtasks']])}

## Dependencies
{chr(10).join([f"- {dep}" for dep in task_def['dependencies']]) if task_def['dependencies'] else "- None"}

## Estimated Effort
**Time**: {task_def['estimated_time']}
**Complexity**: {task_def['complexity']}
**Priority**: {task_def['priority']}

## Deliverables
{chr(10).join([f"- {deliverable}" for deliverable in task_def['deliverables']])}

## Quality Gates
{chr(10).join([f"- {gate}" for gate in task_def['quality_gates']])}

## Notes
{task_def['notes']}

---
*Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""

            task_files_data.append({
                "name": f"Task{i}.md",
                "content": task_content,
                "task_number": i
            })

        # Generate tasks index
        project_name = project_context.get("project_name", "Project")
        index_content = generate_tasks_index(project_name, task_definitions)
        task_files_data.append({
            "name": "TASKS_INDEX.md",
            "content": index_content
        })

        # Save task files to database
        task_file_ids = await file_storage_service.save_task_files(
            project_id=project_id,
            task_files=task_files_data,
            agents_used=agents_used,
            generation_context=project_context
        )

        logger.info(f"Generated and saved {len(task_file_ids)} task files to database")

        # Return list of file IDs for compatibility
        all_file_ids = [overview_file_id] + task_file_ids
        logger.info(f"Generated {len(all_file_ids)} files total for project {project_id}")
        return all_file_ids

    except Exception as e:
        logger.error(f"Failed to generate project files: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []


def generate_project_overview_content(project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> str:
    """Generate ProjectOverview.md content from orchestration results."""
    project_name = project_context.get("project_name", "Untitled Project")
    project_description = project_context.get("project_description", "No description provided")
    requirements = project_context.get("requirements", "No requirements specified")
    tech_stack = project_context.get("tech_stack", [])

    # Extract insights from agent outputs
    executive_summary = ""
    technical_architecture = ""
    implementation_plan = ""
    risk_assessment = ""
    resource_requirements = ""
    timeline_estimate = ""

    # Process agent outputs to extract relevant content
    for agent_id, output in agent_outputs.items():
        result_text = ""
        if isinstance(output, dict):
            result_text = output.get("result", str(output))
        else:
            result_text = str(output)

        # Extract content based on agent type and result content
        if "architect" in agent_id.lower() or "technical" in result_text.lower():
            if not technical_architecture:
                technical_architecture = result_text[:1000] + "..." if len(result_text) > 1000 else result_text
        elif "business" in agent_id.lower() or "analyst" in agent_id.lower():
            if not executive_summary:
                executive_summary = result_text[:1000] + "..." if len(result_text) > 1000 else result_text
        elif "project" in agent_id.lower() or "manager" in agent_id.lower():
            if not implementation_plan:
                implementation_plan = result_text[:1000] + "..." if len(result_text) > 1000 else result_text
        elif "qa" in agent_id.lower() or "quality" in agent_id.lower():
            if not risk_assessment:
                risk_assessment = result_text[:1000] + "..." if len(result_text) > 1000 else result_text
        elif "resource" in agent_id.lower() or "devops" in agent_id.lower():
            if not resource_requirements:
                resource_requirements = result_text[:1000] + "..." if len(result_text) > 1000 else result_text
        elif not timeline_estimate:
            timeline_estimate = result_text[:1000] + "..." if len(result_text) > 1000 else result_text

    for step_id, output in agent_outputs.items():
        result = output.get("result", "")
        agent_id = output.get("agent_id", "")

        if "executive" in step_id.lower() or "summary" in step_id.lower():
            executive_summary += f"\n### From {agent_id}:\n{result}\n"
        elif "technical" in step_id.lower() or "architecture" in step_id.lower():
            technical_architecture += f"\n### From {agent_id}:\n{result}\n"
        elif "implementation" in step_id.lower() or "plan" in step_id.lower():
            implementation_plan += f"\n### From {agent_id}:\n{result}\n"
        elif "risk" in step_id.lower():
            risk_assessment += f"\n### From {agent_id}:\n{result}\n"
        elif "resource" in step_id.lower():
            resource_requirements += f"\n### From {agent_id}:\n{result}\n"
        elif "timeline" in step_id.lower():
            timeline_estimate += f"\n### From {agent_id}:\n{result}\n"

    # If no specific sections found, use general analysis organized by agent
    if not any([executive_summary, technical_architecture, implementation_plan]):
        for step_id, output in agent_outputs.items():
            agent_id = output.get("agent_id", "unknown")
            result = output.get("result", "")
            agent_name = agent_id.replace('_', ' ').title()

            executive_summary += f"\n### Analysis from {agent_name}:\n{result}\n\n"

    # Provide fallback content if no agent outputs are available
    if not agent_outputs or not any([executive_summary, technical_architecture, implementation_plan]):
        executive_summary = f"""
### Project Analysis

The {project_name} project represents a comprehensive initiative requiring careful planning and execution. Based on the provided requirements and technology stack, this project involves:

**Key Objectives:**
- {project_description}
- Implementation using {', '.join(tech_stack) if tech_stack else 'modern technologies'}
- Meeting specified requirements and constraints

**Strategic Approach:**
- Systematic analysis of requirements
- Technology-driven solution design
- Iterative development methodology
- Quality assurance and testing integration
"""

        technical_architecture = f"""
### Architecture Overview

The technical architecture for {project_name} should incorporate:

**Technology Stack:**
{chr(10).join([f"- {tech}" for tech in tech_stack]) if tech_stack else "- Modern, scalable technologies"}

**Architectural Principles:**
- Modular design for maintainability
- Scalable infrastructure
- Security-first approach
- Performance optimization
- Cross-platform compatibility

**System Components:**
- Frontend user interface
- Backend services and APIs
- Data storage and management
- Integration layers
- Monitoring and logging
"""

        implementation_plan = f"""
### Implementation Strategy

**Phase 1: Foundation**
- Project setup and environment configuration
- Core architecture implementation
- Basic functionality development

**Phase 2: Feature Development**
- Core feature implementation
- User interface development
- API integration

**Phase 3: Testing and Optimization**
- Comprehensive testing
- Performance optimization
- Security validation

**Phase 4: Deployment and Launch**
- Production deployment
- User training and documentation
- Monitoring and maintenance setup
"""

    content = f"""# {project_name} - Project Overview

## Project Information
- **Name**: {project_name}
- **Description**: {project_description}
- **Technology Stack**: {', '.join(tech_stack) if tech_stack else 'Not specified'}
- **Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Executive Summary
{executive_summary or "No executive summary available from agent analysis."}

## Technical Architecture
{technical_architecture or "No technical architecture details available from agent analysis."}

## Implementation Plan
{implementation_plan or "No implementation plan available from agent analysis."}

## Risk Assessment
{risk_assessment or "No risk assessment available from agent analysis."}

## Resource Requirements
{resource_requirements or "No resource requirements available from agent analysis."}

## Timeline Estimate
{timeline_estimate or "No timeline estimate available from agent analysis."}

## Requirements
{requirements}

## Agent Collaboration Summary
This project overview was generated through multi-agent collaboration involving:
{chr(10).join([f"- {output.get('agent_id', 'Unknown Agent')}" for output in agent_outputs.values()])}

Each agent contributed their specialized expertise to create this comprehensive project overview.
"""

    return content


def generate_task_files(project_context: Dict[str, Any], agent_outputs: Dict[str, Any], project_dir) -> List[str]:
    """Generate separate task files from orchestration results."""
    project_name = project_context.get("project_name", "Untitled Project")
    project_description = project_context.get("project_description", "")
    requirements = project_context.get("requirements", "")
    tech_stack = project_context.get("tech_stack", [])

    files_generated = []

    # Define comprehensive task structure based on project type and requirements
    task_definitions = generate_comprehensive_tasks(project_context, agent_outputs)

    # Generate individual task files
    for i, task_def in enumerate(task_definitions, 1):
        task_file = project_dir / f"Task{i}.md"

        task_content = f"""# Task {i}: {task_def['title']}

## Description
{task_def['description']}

## Acceptance Criteria
{chr(10).join([f"- {criteria}" for criteria in task_def['acceptance_criteria']])}

## Technical Requirements
{chr(10).join([f"- {req}" for req in task_def['technical_requirements']])}

## Implementation Steps
{chr(10).join([f"{j}. {step}" for j, step in enumerate(task_def['implementation_steps'], 1)])}

## Subtasks
{chr(10).join([f"- [ ] {subtask}" for subtask in task_def['subtasks']])}

## Dependencies
{chr(10).join([f"- {dep}" for dep in task_def['dependencies']]) if task_def['dependencies'] else "- None"}

## Estimated Effort
**Time**: {task_def['estimated_time']}
**Complexity**: {task_def['complexity']}
**Priority**: {task_def['priority']}

## Deliverables
{chr(10).join([f"- {deliverable}" for deliverable in task_def['deliverables']])}

## Quality Gates
{chr(10).join([f"- {gate}" for gate in task_def['quality_gates']])}

## Notes
{task_def['notes']}

---
*Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""

        logger.info(f"Writing {task_file.name}")
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(task_content)
        files_generated.append(str(task_file))
        logger.info(f"{task_file.name} written successfully ({len(task_content)} characters)")

    # Also generate a main tasks index file
    index_file = project_dir / "TASKS_INDEX.md"
    index_content = generate_tasks_index(project_name, task_definitions)

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    files_generated.append(str(index_file))

    return files_generated


def generate_comprehensive_tasks(project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate intelligent task definitions based on actual project requirements and context."""
    project_name = project_context.get("project_name", "Untitled Project")
    project_description = project_context.get("project_description", "")
    tech_stack = project_context.get("tech_stack", [])
    requirements = project_context.get("requirements", "")

    # Analyze the actual project to determine what tasks are needed
    if "campus" in project_name.lower() or "campus" in project_description.lower():
        return generate_campus_management_tasks(project_context, agent_outputs)
    elif any(keyword in requirements.lower() for keyword in ['ecommerce', 'shop', 'store', 'marketplace']):
        return generate_ecommerce_tasks(project_context, agent_outputs)
    elif any(keyword in requirements.lower() for keyword in ['blog', 'cms', 'content']):
        return generate_cms_tasks(project_context, agent_outputs)
    elif any(keyword in requirements.lower() for keyword in ['chat', 'messaging', 'communication']):
        return generate_messaging_tasks(project_context, agent_outputs)
    elif any(keyword in tech_stack for keyword in ['flutter', 'react-native', 'mobile']):
        return generate_mobile_app_tasks(project_context, agent_outputs)
    elif any(keyword in tech_stack for keyword in ['react', 'vue', 'angular', 'frontend']):
        return generate_web_app_tasks(project_context, agent_outputs)
    elif any(keyword in tech_stack for keyword in ['fastapi', 'django', 'flask', 'express', 'api']):
        return generate_api_tasks(project_context, agent_outputs)
    else:
        # Intelligent analysis of requirements to generate specific tasks
        return generate_intelligent_tasks_from_requirements(project_context, agent_outputs)


def generate_campus_management_tasks(project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate specific tasks for Campus Pilot management system."""
    project_name = project_context.get("project_name", "Campus Management System")
    tech_stack = project_context.get("tech_stack", [])
    requirements = project_context.get("requirements", "")

    # Extract specific features from requirements
    has_admin_flow = "admin" in requirements.lower()
    has_teacher_flow = "teacher" in requirements.lower()
    has_parent_flow = "parent" in requirements.lower()
    has_flutter = "flutter" in str(tech_stack).lower()
    has_aws = "aws" in str(tech_stack).lower()
    has_cognito = "cognito" in str(tech_stack).lower()

    tasks = [
        {
            "title": "AWS Infrastructure and Cognito Authentication Setup",
            "description": f"Set up AWS infrastructure for {project_name} including Cognito user pools, Amplify configuration, and Lambda functions for backend services.",
            "acceptance_criteria": [
                "AWS Cognito user pools configured for Admin, Teacher, and Parent roles",
                "AWS Amplify project set up and connected to Flutter app",
                "Lambda functions deployed for core backend operations",
                "DynamoDB tables created with proper schema",
                "SAML integration configured for institutional SSO"
            ],
            "technical_requirements": [
                "Configure AWS Cognito with custom attributes for user roles",
                "Set up Amplify CLI and configure Flutter project",
                "Create DynamoDB tables for users, campuses, classes, students, etc.",
                "Implement Lambda functions for business logic",
                "Configure SAML identity provider integration"
            ],
            "implementation_steps": [
                "Create AWS account and set up IAM roles",
                "Configure Cognito User Pool with custom attributes",
                "Set up Amplify project and connect to Flutter",
                "Design and create DynamoDB table schema",
                "Implement core Lambda functions",
                "Configure SAML integration for institutional login"
            ],
            "subtasks": [
                "Create AWS Cognito User Pool with Admin/Teacher/Parent groups",
                "Configure Cognito custom attributes (campus_id, role, profile_data)",
                "Set up AWS Amplify project and configure authentication",
                "Create DynamoDB tables: Users, Campuses, Classes, Students, Attendance, etc.",
                "Implement Lambda functions for user management and profile switching",
                "Configure SAML identity provider for institutional SSO",
                "Set up API Gateway for Lambda function endpoints",
                "Configure Amplify DataStore for offline capabilities",
                "Set up CloudWatch logging and monitoring",
                "Create development and production environments"
            ],
            "dependencies": [],
            "estimated_time": "2-3 weeks",
            "complexity": "High",
            "priority": "Critical",
            "deliverables": [
                "Configured AWS Cognito with role-based access",
                "Amplify project connected to Flutter app",
                "DynamoDB schema with all required tables",
                "Core Lambda functions for authentication and user management",
                "SAML integration for institutional login"
            ],
            "quality_gates": [
                "User registration and login working for all roles",
                "Profile switching functionality operational",
                "DynamoDB queries performing efficiently",
                "Lambda functions passing all tests",
                "SAML authentication working with test institution"
            ],
            "notes": "This is the foundation for the entire campus management system. All user flows depend on this infrastructure."
        },
        {
            "title": "Flutter App Foundation and Multi-Profile System",
            "description": f"Create the Flutter application foundation with multi-profile support, allowing users to have Admin, Teacher, and Parent profiles within the same account.",
            "acceptance_criteria": [
                "Flutter app with proper project structure and navigation",
                "Multi-profile system allowing users to switch between roles",
                "Automatic profile selection and dashboard redirection",
                "Profile creation flow for new users",
                "Secure session management and state persistence"
            ],
            "technical_requirements": [
                "Flutter project with clean architecture pattern",
                "State management using Provider or Riverpod",
                "Secure storage for user sessions and profile data",
                "Navigation system supporting role-based routing",
                "Amplify Flutter integration for authentication"
            ],
            "implementation_steps": [
                "Create Flutter project with proper folder structure",
                "Implement authentication screens (register/login)",
                "Build profile selection and creation system",
                "Create role-based dashboard navigation",
                "Implement secure session management"
            ],
            "subtasks": [
                "Initialize Flutter project with clean architecture",
                "Set up state management (Provider/Riverpod/Bloc)",
                "Create authentication screens (Register, Login, Forgot Password)",
                "Implement profile selection screen with role switching",
                "Build profile creation flow for Admin/Teacher/Parent",
                "Create role-based dashboard screens",
                "Implement automatic profile redirection on app restart",
                "Set up secure storage for user sessions",
                "Create common widgets and UI components",
                "Implement navigation system with role-based routing",
                "Add form validation and error handling",
                "Set up app theming and responsive design"
            ],
            "dependencies": ["Task 1: AWS Infrastructure and Cognito Authentication Setup"],
            "estimated_time": "3-4 weeks",
            "complexity": "High",
            "priority": "Critical",
            "deliverables": [
                "Flutter app with authentication system",
                "Multi-profile management system",
                "Role-based dashboard navigation",
                "Secure session management",
                "Responsive UI components"
            ],
            "quality_gates": [
                "Users can register and login successfully",
                "Profile switching works seamlessly",
                "App remembers selected profile on restart",
                "All authentication flows tested and working",
                "UI is responsive across different screen sizes"
            ],
            "notes": "The multi-profile system is unique to this campus management platform and critical for user experience."
        }
    ]

    # Add role-specific tasks based on requirements
    if has_admin_flow:
        tasks.append(generate_admin_management_task())

    if has_teacher_flow:
        tasks.append(generate_teacher_functionality_task())

    if has_parent_flow:
        tasks.append(generate_parent_functionality_task())

    # Add supporting tasks
    tasks.extend([
        generate_academic_year_management_task(),
        generate_communication_system_task(),
        generate_attendance_system_task(),
        generate_fee_management_task(),
        generate_testing_and_deployment_task()
    ])

    return tasks


def generate_admin_management_task() -> Dict[str, Any]:
    """Generate admin-specific functionality task for campus management."""
    return {
        "title": "Admin Dashboard and Campus Management Features",
        "description": "Implement comprehensive admin functionality including campus setup, user management, academic planning, and administrative controls.",
        "acceptance_criteria": [
            "Admin can setup and configure campus settings",
            "Profile approval/deactivation system working",
            "Academic year structure can be defined and managed",
            "Class and subject management fully functional",
            "Teacher and student assignment systems operational",
            "Timetable generation and management working",
            "Leave approval system functional",
            "Communication system for targeted notifications",
            "Transportation and fee management implemented"
        ],
        "technical_requirements": [
            "Admin dashboard with comprehensive controls",
            "Campus configuration and settings management",
            "User profile approval workflow",
            "Academic year and class management system",
            "Teacher-subject assignment logic",
            "Automated timetable generation",
            "Leave request approval system",
            "Notification system with targeting capabilities",
            "Transportation and fee management modules"
        ],
        "implementation_steps": [
            "Create admin dashboard with navigation menu",
            "Implement campus setup and configuration screens",
            "Build user profile approval/deactivation system",
            "Create academic year and class management",
            "Implement teacher-subject assignment interface",
            "Build timetable generation and management",
            "Create leave approval workflow",
            "Implement targeted notification system",
            "Add transportation and fee management"
        ],
        "subtasks": [
            "Create admin dashboard with role-based navigation",
            "Implement campus setup form (name, address, academic calendar)",
            "Build user profile approval interface with bulk actions",
            "Create academic year definition with terms/semesters",
            "Implement class creation with sections and capacity",
            "Build subject management with curriculum mapping",
            "Create teacher-subject assignment with conflict detection",
            "Implement class teacher assignment (one per class)",
            "Build student-class assignment with bulk import",
            "Create automated timetable generation algorithm",
            "Implement manual timetable editing and conflict resolution",
            "Build leave request approval dashboard with filters",
            "Create notification composer with targeting options",
            "Implement transportation route and driver management",
            "Build fee structure definition with due dates",
            "Create exam timetable and holiday management",
            "Add academic activity planning interface",
            "Implement bulk operations for efficiency"
        ],
        "dependencies": ["Task 2: Flutter App Foundation and Multi-Profile System"],
        "estimated_time": "4-5 weeks",
        "complexity": "Very High",
        "priority": "Critical",
        "deliverables": [
            "Complete admin dashboard",
            "Campus configuration system",
            "User management interface",
            "Academic planning tools",
            "Timetable management system",
            "Communication and notification system"
        ],
        "quality_gates": [
            "All admin workflows tested and functional",
            "Timetable generation produces conflict-free schedules",
            "Notification targeting works accurately",
            "Bulk operations perform efficiently",
            "User interface is intuitive for administrators"
        ],
        "notes": "This is the most complex task as it includes all administrative functions that control the entire campus ecosystem."
    }


def generate_teacher_functionality_task() -> Dict[str, Any]:
    """Generate teacher-specific functionality task."""
    return {
        "title": "Teacher Dashboard and Classroom Management",
        "description": "Implement teacher-specific features including class access, attendance management, daily activities, assessment, and communication tools.",
        "acceptance_criteria": [
            "Teachers can access assigned classes and subjects",
            "Student approval system for class enrollment",
            "Weekly attendance marking with default present status",
            "Daily diary for tasks and homework entries",
            "Assessment and grading system functional",
            "Quarterly and half-yearly result publication",
            "Class and individual student communication",
            "Leave request approval for students",
            "Personal leave request submission"
        ],
        "technical_requirements": [
            "Teacher dashboard with class overview",
            "Class and subject access control",
            "Attendance management with calendar interface",
            "Daily diary system with task creation",
            "Assessment and grading interface",
            "Result publication system",
            "Communication tools for students",
            "Leave management workflow",
            "Information access for academic calendar"
        ],
        "implementation_steps": [
            "Create teacher dashboard with assigned classes",
            "Implement class access and student management",
            "Build attendance marking system with calendar",
            "Create daily diary and homework management",
            "Implement assessment and grading tools",
            "Build result publication system",
            "Create communication interface",
            "Implement leave management features"
        ],
        "subtasks": [
            "Create teacher dashboard showing assigned classes/subjects",
            "Implement class access with student list view",
            "Build student approval interface for class enrollment",
            "Create weekly calendar for attendance marking",
            "Implement attendance interface with default present status",
            "Build daily diary with task and homework creation",
            "Create assessment interface for marking tasks/exams",
            "Implement grading system with rubrics",
            "Build result publication for quarterly/half-yearly exams",
            "Create class communication for announcements",
            "Implement individual student messaging",
            "Build leave request approval interface with reasons",
            "Create notification viewing for academic events",
            "Implement personal leave request submission",
            "Add academic calendar and holiday viewing",
            "Create attendance analytics and reports"
        ],
        "dependencies": ["Task 3: Admin Dashboard and Campus Management Features"],
        "estimated_time": "3-4 weeks",
        "complexity": "High",
        "priority": "Critical",
        "deliverables": [
            "Teacher dashboard with class management",
            "Attendance marking system",
            "Daily diary and homework management",
            "Assessment and grading tools",
            "Communication interface",
            "Leave management system"
        ],
        "quality_gates": [
            "Attendance marking is efficient and intuitive",
            "Daily diary entries are properly organized",
            "Assessment system handles various grading schemes",
            "Communication reaches intended recipients",
            "Leave approval workflow is streamlined"
        ],
        "notes": "Teacher functionality focuses on daily classroom management and student interaction."
    }


def generate_parent_functionality_task() -> Dict[str, Any]:
    """Generate parent-specific functionality task."""
    return {
        "title": "Parent Dashboard and Student Monitoring",
        "description": "Implement parent-specific features for monitoring student progress, attendance, communication, and academic information access.",
        "acceptance_criteria": [
            "Parents can view daily attendance and overall percentage",
            "Daily diary access with weekly calendar navigation",
            "Result viewing for published assessments",
            "Notification viewing and academic calendar access",
            "Leave request submission for children",
            "Fee structure and due date information",
            "Timetable viewing for student schedule",
            "Homework tracking with completion status"
        ],
        "technical_requirements": [
            "Parent dashboard with student overview",
            "Attendance tracking and analytics",
            "Daily diary viewing with calendar interface",
            "Result viewing system",
            "Communication and notification access",
            "Leave request submission system",
            "Fee information display",
            "Timetable and homework viewing"
        ],
        "implementation_steps": [
            "Create parent dashboard with student information",
            "Implement attendance viewing and analytics",
            "Build daily diary access with calendar",
            "Create result viewing interface",
            "Implement communication and notification viewing",
            "Build leave request submission",
            "Add fee and timetable information access",
            "Create homework tracking interface"
        ],
        "subtasks": [
            "Create parent dashboard with child's overview",
            "Implement daily attendance viewing with calendar",
            "Build attendance percentage calculation and display",
            "Create daily diary viewing with weekly calendar navigation",
            "Implement result viewing for published assessments",
            "Build notification viewing interface",
            "Create academic calendar and holiday viewing",
            "Implement leave request submission with reason",
            "Build fee structure viewing with due dates",
            "Create student timetable viewing",
            "Implement homework viewing with completion status",
            "Add teacher notes and observation viewing",
            "Create progress tracking and analytics",
            "Implement parent-teacher communication interface",
            "Add emergency contact and pickup authorization",
            "Create transportation schedule viewing"
        ],
        "dependencies": ["Task 4: Teacher Dashboard and Classroom Management"],
        "estimated_time": "2-3 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Parent dashboard with student monitoring",
            "Attendance and progress tracking",
            "Communication and notification access",
            "Leave request system",
            "Academic information viewing"
        ],
        "quality_gates": [
            "All student information is accurately displayed",
            "Attendance data is real-time and accurate",
            "Communication system works bidirectionally",
            "Leave requests are properly submitted and tracked",
            "Academic calendar information is up-to-date"
        ],
        "notes": "Parent functionality focuses on transparency and communication between home and school."
    }


def generate_academic_year_management_task() -> Dict[str, Any]:
    """Generate academic year and calendar management task."""
    return {
        "title": "Academic Year Structure and Calendar Management",
        "description": "Implement comprehensive academic year management including terms, holidays, exam schedules, and academic activity planning.",
        "acceptance_criteria": [
            "Academic year structure can be defined with terms/semesters",
            "Holiday calendar management functional",
            "Exam timetable creation and management",
            "Academic activity planning and scheduling",
            "Calendar integration across all user roles"
        ],
        "technical_requirements": [
            "Academic year configuration system",
            "Holiday and event calendar management",
            "Exam scheduling with conflict detection",
            "Activity planning interface",
            "Calendar synchronization across roles"
        ],
        "implementation_steps": [
            "Create academic year definition interface",
            "Implement holiday calendar management",
            "Build exam timetable creation system",
            "Create academic activity planning",
            "Implement calendar integration"
        ],
        "subtasks": [
            "Create academic year setup with start/end dates",
            "Implement term/semester definition",
            "Build holiday calendar with types (national, regional, school)",
            "Create exam timetable with subject scheduling",
            "Implement academic activity planning interface",
            "Build calendar conflict detection",
            "Create calendar views for different roles",
            "Implement calendar notifications and reminders"
        ],
        "dependencies": ["Task 3: Admin Dashboard and Campus Management Features"],
        "estimated_time": "2 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Academic year management system",
            "Holiday and exam calendar",
            "Activity planning interface",
            "Integrated calendar system"
        ],
        "quality_gates": [
            "Academic calendar is consistent across all roles",
            "Exam scheduling prevents conflicts",
            "Holiday calendar is properly maintained",
            "Activity planning is intuitive and functional"
        ],
        "notes": "Academic calendar is the backbone that coordinates all campus activities."
    }


def generate_communication_system_task() -> Dict[str, Any]:
    """Generate communication and notification system task."""
    return {
        "title": "Communication and Notification System",
        "description": "Implement comprehensive communication system with targeted notifications, announcements, and messaging between different user roles.",
        "acceptance_criteria": [
            "Targeted notification system for different user groups",
            "Announcement system for campus-wide communication",
            "Direct messaging between teachers and parents",
            "Notification delivery tracking and read receipts",
            "Emergency communication capabilities"
        ],
        "technical_requirements": [
            "Push notification system with targeting",
            "Message composition with rich text support",
            "Delivery tracking and analytics",
            "Emergency alert system",
            "Message archiving and search"
        ],
        "implementation_steps": [
            "Implement push notification infrastructure",
            "Create message composition interface",
            "Build targeting and delivery system",
            "Implement emergency communication",
            "Add message tracking and analytics"
        ],
        "subtasks": [
            "Set up Firebase Cloud Messaging for push notifications",
            "Create notification targeting system (all, teachers, specific class, individual)",
            "Implement message composition with rich text editor",
            "Build notification delivery tracking",
            "Create emergency alert system with priority levels",
            "Implement message archiving and search",
            "Add read receipt functionality",
            "Create notification preferences for users",
            "Implement scheduled notifications",
            "Build communication analytics dashboard"
        ],
        "dependencies": ["Task 4: Teacher Dashboard and Classroom Management"],
        "estimated_time": "2-3 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Push notification system",
            "Targeted messaging interface",
            "Emergency communication system",
            "Message tracking and analytics"
        ],
        "quality_gates": [
            "Notifications are delivered reliably",
            "Targeting system works accurately",
            "Emergency alerts have priority delivery",
            "Message tracking provides accurate analytics"
        ],
        "notes": "Effective communication is crucial for campus coordination and parent engagement."
    }


def generate_attendance_system_task() -> Dict[str, Any]:
    """Generate attendance management system task."""
    return {
        "title": "Attendance Management and Analytics System",
        "description": "Implement comprehensive attendance tracking with teacher marking interface, parent viewing, and analytics reporting.",
        "acceptance_criteria": [
            "Teachers can mark attendance efficiently with default present status",
            "Parents can view daily and overall attendance",
            "Attendance analytics and reporting functional",
            "Attendance alerts for low attendance",
            "Integration with academic calendar"
        ],
        "technical_requirements": [
            "Attendance marking interface with calendar",
            "Attendance analytics and calculations",
            "Real-time attendance updates",
            "Attendance reporting system",
            "Alert system for attendance issues"
        ],
        "implementation_steps": [
            "Create attendance marking interface for teachers",
            "Implement attendance viewing for parents",
            "Build attendance analytics and reporting",
            "Create attendance alert system",
            "Integrate with academic calendar"
        ],
        "subtasks": [
            "Create weekly calendar interface for attendance marking",
            "Implement default present status with absent marking",
            "Build bulk attendance operations",
            "Create attendance percentage calculations",
            "Implement attendance analytics dashboard",
            "Build attendance reports for different periods",
            "Create low attendance alerts for parents and admin",
            "Implement attendance trends and patterns analysis",
            "Add attendance export functionality",
            "Create attendance correction interface for errors"
        ],
        "dependencies": ["Task 5: Parent Dashboard and Student Monitoring"],
        "estimated_time": "2 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Attendance marking system",
            "Attendance analytics dashboard",
            "Parent attendance viewing",
            "Attendance reporting system"
        ],
        "quality_gates": [
            "Attendance marking is fast and intuitive",
            "Attendance calculations are accurate",
            "Analytics provide meaningful insights",
            "Alerts are triggered appropriately"
        ],
        "notes": "Attendance tracking is a daily operation that must be efficient and accurate."
    }


def generate_fee_management_task() -> Dict[str, Any]:
    """Generate fee management system task."""
    return {
        "title": "Fee Management and Payment Tracking",
        "description": "Implement fee structure management, payment tracking, and financial reporting for campus administration.",
        "acceptance_criteria": [
            "Fee structure can be defined per class with due dates",
            "Payment tracking and receipt generation",
            "Fee reminders and overdue notifications",
            "Financial reporting and analytics",
            "Integration with payment gateways"
        ],
        "technical_requirements": [
            "Fee structure configuration system",
            "Payment tracking and receipt system",
            "Automated reminder system",
            "Financial reporting dashboard",
            "Payment gateway integration"
        ],
        "implementation_steps": [
            "Create fee structure definition interface",
            "Implement payment tracking system",
            "Build automated reminder system",
            "Create financial reporting dashboard",
            "Integrate payment gateways"
        ],
        "subtasks": [
            "Create fee structure setup per class/grade",
            "Implement fee breakdown with categories",
            "Build payment tracking with receipt generation",
            "Create automated fee reminder system",
            "Implement overdue payment notifications",
            "Build financial dashboard for admin",
            "Create payment history for parents",
            "Implement fee collection reports",
            "Add payment gateway integration (Razorpay, etc.)",
            "Create fee defaulter tracking and reports"
        ],
        "dependencies": ["Task 6: Academic Year Structure and Calendar Management"],
        "estimated_time": "2-3 weeks",
        "complexity": "Medium",
        "priority": "Medium",
        "deliverables": [
            "Fee structure management",
            "Payment tracking system",
            "Financial reporting dashboard",
            "Payment gateway integration"
        ],
        "quality_gates": [
            "Fee calculations are accurate",
            "Payment tracking is reliable",
            "Reminders are sent timely",
            "Financial reports are comprehensive"
        ],
        "notes": "Fee management is crucial for campus financial operations and parent transparency."
    }


def generate_testing_and_deployment_task() -> Dict[str, Any]:
    """Generate testing and deployment task for campus management system."""
    return {
        "title": "Testing, Quality Assurance, and Production Deployment",
        "description": "Comprehensive testing of all campus management features, performance optimization, and production deployment with monitoring.",
        "acceptance_criteria": [
            "All user workflows tested across Admin, Teacher, and Parent roles",
            "Performance testing under realistic load",
            "Security testing for data protection and privacy",
            "Production deployment with monitoring",
            "User training and documentation complete"
        ],
        "technical_requirements": [
            "Automated testing for all user flows",
            "Performance testing with realistic data",
            "Security audit and penetration testing",
            "Production deployment pipeline",
            "Monitoring and alerting system"
        ],
        "implementation_steps": [
            "Create comprehensive test suite",
            "Perform load and performance testing",
            "Conduct security audit",
            "Deploy to production environment",
            "Set up monitoring and support"
        ],
        "subtasks": [
            "Create unit tests for all business logic",
            "Implement integration tests for API endpoints",
            "Build end-to-end tests for user workflows",
            "Perform load testing with realistic user scenarios",
            "Conduct security audit focusing on student data protection",
            "Test multi-profile switching and role-based access",
            "Validate attendance and grading calculations",
            "Test notification delivery and targeting",
            "Perform cross-platform testing (iOS/Android)",
            "Set up production AWS environment",
            "Configure monitoring and alerting",
            "Create user training materials and documentation",
            "Conduct user acceptance testing with real schools",
            "Set up backup and disaster recovery procedures"
        ],
        "dependencies": ["Task 9: Fee Management and Payment Tracking"],
        "estimated_time": "3-4 weeks",
        "complexity": "High",
        "priority": "Critical",
        "deliverables": [
            "Comprehensive test suite",
            "Performance and security audit reports",
            "Production deployment",
            "Monitoring and alerting system",
            "User documentation and training materials"
        ],
        "quality_gates": [
            "All tests passing with 90%+ coverage",
            "Performance meets requirements under load",
            "Security audit shows no critical vulnerabilities",
            "Production deployment is stable",
            "User training is effective"
        ],
        "notes": "Quality assurance is critical for a system handling sensitive student and academic data."
    }


def extract_agent_insights(agent_outputs: Dict[str, Any]) -> Dict[str, str]:
    """Extract key insights from agent outputs."""
    insights = {}

    for step_id, output in agent_outputs.items():
        if isinstance(output, dict):
            agent_id = output.get("agent_id", "")
            result = output.get("result", "")
            if agent_id and result:
                insights[agent_id] = result
        else:
            # Handle direct string results
            insights[step_id] = str(output)

    return insights


def generate_intelligent_tasks_from_requirements(project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate intelligent tasks by analyzing project requirements and tech stack."""
    project_name = project_context.get("project_name", "Project")
    requirements = project_context.get("requirements", "").lower()
    tech_stack = project_context.get("tech_stack", [])

    # Analyze requirements to extract key features
    features = []
    if any(word in requirements for word in ['user', 'login', 'register', 'auth']):
        features.append('authentication')
    if any(word in requirements for word in ['dashboard', 'admin', 'manage']):
        features.append('admin_panel')
    if any(word in requirements for word in ['api', 'endpoint', 'backend']):
        features.append('api')
    if any(word in requirements for word in ['database', 'data', 'store']):
        features.append('database')
    if any(word in requirements for word in ['ui', 'interface', 'frontend']):
        features.append('frontend')
    if any(word in requirements for word in ['test', 'quality']):
        features.append('testing')
    if any(word in requirements for word in ['deploy', 'production', 'hosting']):
        features.append('deployment')

    tasks = []

    # Generate setup task
    tasks.append({
        "title": f"{project_name} - Project Setup and Infrastructure",
        "description": f"Set up the development environment and infrastructure for {project_name} using {', '.join(tech_stack[:3]) if tech_stack else 'modern technologies'}.",
        "acceptance_criteria": [
            "Development environment is configured and functional",
            "Project structure follows best practices",
            "Version control and CI/CD pipeline set up",
            "All team members can run the project locally"
        ],
        "technical_requirements": [
            f"Configure {', '.join(tech_stack[:3]) if tech_stack else 'development'} environment",
            "Set up project structure and dependencies",
            "Configure development tools and linting",
            "Set up version control and deployment pipeline"
        ],
        "implementation_steps": [
            "Initialize project with proper structure",
            "Configure development environment",
            "Set up dependencies and package management",
            "Configure CI/CD pipeline",
            "Create development documentation"
        ],
        "subtasks": [
            f"Initialize {tech_stack[0] if tech_stack else 'project'} project structure",
            "Set up package management and dependencies",
            "Configure development tools (linting, formatting)",
            "Set up version control (Git) with proper branching",
            "Configure CI/CD pipeline",
            "Create environment configuration",
            "Set up development database/storage",
            "Write setup and installation documentation"
        ],
        "dependencies": [],
        "estimated_time": "1-2 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Configured development environment",
            "Project repository with CI/CD",
            "Development documentation",
            "Team onboarding guide"
        ],
        "quality_gates": [
            "All team members can set up project locally",
            "CI/CD pipeline passes all checks",
            "Code quality tools are working",
            "Documentation is complete"
        ],
        "notes": f"Foundation setup for {project_name} using {', '.join(tech_stack) if tech_stack else 'specified technologies'}."
    })

    # Generate feature-specific tasks based on analysis
    if 'authentication' in features:
        tasks.append(generate_auth_task_from_requirements(project_context))
    if 'database' in features:
        tasks.append(generate_database_task_from_requirements(project_context))
    if 'api' in features:
        tasks.append(generate_api_task_from_requirements(project_context))
    if 'frontend' in features:
        tasks.append(generate_frontend_task_from_requirements(project_context))
    if 'admin_panel' in features:
        tasks.append(generate_admin_task_from_requirements(project_context))
    if 'testing' in features:
        tasks.append(generate_testing_task_from_requirements(project_context))
    if 'deployment' in features:
        tasks.append(generate_deployment_task_from_requirements(project_context))

    return tasks


def generate_ecommerce_tasks(project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate tasks for e-commerce projects."""
    # Placeholder for e-commerce specific tasks
    return generate_intelligent_tasks_from_requirements(project_context, agent_outputs)


def generate_cms_tasks(project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate tasks for CMS projects."""
    # Placeholder for CMS specific tasks
    return generate_intelligent_tasks_from_requirements(project_context, agent_outputs)


def generate_messaging_tasks(project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate tasks for messaging/chat projects."""
    # Placeholder for messaging specific tasks
    return generate_intelligent_tasks_from_requirements(project_context, agent_outputs)


def generate_mobile_app_tasks(project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate tasks for mobile app projects."""
    # Placeholder for mobile app specific tasks
    return generate_intelligent_tasks_from_requirements(project_context, agent_outputs)


def generate_web_app_tasks(project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate tasks for web application projects."""
    # Placeholder for web app specific tasks
    return generate_intelligent_tasks_from_requirements(project_context, agent_outputs)


def generate_api_tasks(project_context: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate tasks for API projects."""
    # Placeholder for API specific tasks
    return generate_intelligent_tasks_from_requirements(project_context, agent_outputs)


def generate_auth_task_from_requirements(project_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate authentication task based on project requirements."""
    project_name = project_context.get("project_name", "Project")
    tech_stack = project_context.get("tech_stack", [])

    return {
        "title": f"{project_name} - Authentication and User Management",
        "description": f"Implement user authentication and authorization system for {project_name}.",
        "acceptance_criteria": [
            "Users can register and login securely",
            "Password security follows best practices",
            "Session management is implemented",
            "User roles and permissions are functional"
        ],
        "technical_requirements": [
            f"Implement authentication using {', '.join([t for t in tech_stack if t.lower() in ['jwt', 'oauth', 'cognito', 'auth0']]) or 'secure authentication'}",
            "Set up password hashing and validation",
            "Create user session management",
            "Implement role-based access control"
        ],
        "implementation_steps": [
            "Design user authentication flow",
            "Implement registration and login",
            "Set up session management",
            "Create role-based permissions",
            "Add security measures"
        ],
        "subtasks": [
            "Create user registration form and validation",
            "Implement secure login system",
            "Set up password hashing and storage",
            "Create session management",
            "Implement role-based access control",
            "Add password reset functionality",
            "Set up email verification",
            "Implement logout and session cleanup",
            "Add security headers and CSRF protection",
            "Create user profile management"
        ],
        "dependencies": ["Task 1: Project Setup and Infrastructure"],
        "estimated_time": "2-3 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Authentication system",
            "User management interface",
            "Security documentation",
            "Role-based access control"
        ],
        "quality_gates": [
            "Security testing passes",
            "Authentication flows work correctly",
            "Password security meets standards",
            "Session management is secure"
        ],
        "notes": f"Authentication system tailored for {project_name} requirements."
    }


def generate_database_task_from_requirements(project_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate database task based on project requirements."""
    project_name = project_context.get("project_name", "Project")
    tech_stack = project_context.get("tech_stack", [])

    db_tech = next((t for t in tech_stack if t.lower() in ['mysql', 'postgresql', 'mongodb', 'dynamodb', 'sqlite']), 'database')

    return {
        "title": f"{project_name} - Database Design and Implementation",
        "description": f"Design and implement the database schema and data layer for {project_name} using {db_tech}.",
        "acceptance_criteria": [
            "Database schema is designed and implemented",
            "Data models are properly structured",
            "Database operations are optimized",
            "Data integrity and security are maintained"
        ],
        "technical_requirements": [
            f"Set up {db_tech} database",
            "Design normalized database schema",
            "Implement data access layer",
            "Set up database migrations and seeding"
        ],
        "implementation_steps": [
            "Analyze data requirements",
            "Design database schema",
            "Implement data models",
            "Create database operations",
            "Set up migrations and seeding"
        ],
        "subtasks": [
            f"Set up {db_tech} database instance",
            "Design entity relationship diagram",
            "Create database tables and relationships",
            "Implement data models and validation",
            "Create database migration scripts",
            "Set up database seeding for development",
            "Implement CRUD operations",
            "Add database indexing for performance",
            "Set up database backup procedures",
            "Create database documentation"
        ],
        "dependencies": ["Task 1: Project Setup and Infrastructure"],
        "estimated_time": "2-3 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Database schema and migrations",
            "Data models and validation",
            "Database operations layer",
            "Database documentation"
        ],
        "quality_gates": [
            "Database schema is normalized and efficient",
            "All CRUD operations work correctly",
            "Database performance meets requirements",
            "Data integrity constraints are enforced"
        ],
        "notes": f"Database implementation using {db_tech} for {project_name}."
    }


def generate_api_task_from_requirements(project_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate API task based on project requirements."""
    project_name = project_context.get("project_name", "Project")
    tech_stack = project_context.get("tech_stack", [])

    api_tech = next((t for t in tech_stack if t.lower() in ['fastapi', 'django', 'flask', 'express', 'lambda']), 'REST API')

    return {
        "title": f"{project_name} - API Development and Integration",
        "description": f"Develop REST API endpoints and business logic for {project_name} using {api_tech}.",
        "acceptance_criteria": [
            "All required API endpoints are implemented",
            "API documentation is complete and accurate",
            "Error handling and validation are comprehensive",
            "API performance meets requirements"
        ],
        "technical_requirements": [
            f"Implement REST API using {api_tech}",
            "Create comprehensive input validation",
            "Implement proper error handling",
            "Set up API documentation"
        ],
        "implementation_steps": [
            "Design API structure and endpoints",
            "Implement core business logic",
            "Create API endpoints with validation",
            "Add error handling and logging",
            "Generate API documentation"
        ],
        "subtasks": [
            f"Set up {api_tech} project structure",
            "Design API endpoints and data contracts",
            "Implement business logic and services",
            "Create input validation schemas",
            "Implement error handling middleware",
            "Add logging and monitoring",
            "Create API documentation (OpenAPI/Swagger)",
            "Implement rate limiting and security",
            "Add API testing and validation",
            "Set up API versioning"
        ],
        "dependencies": ["Task 2: Database Design and Implementation"],
        "estimated_time": "3-4 weeks",
        "complexity": "High",
        "priority": "High",
        "deliverables": [
            "Complete REST API",
            "Business logic implementation",
            "API documentation",
            "Error handling system"
        ],
        "quality_gates": [
            "All API endpoints are functional",
            "API documentation is accurate",
            "Error handling covers all scenarios",
            "API performance meets requirements"
        ],
        "notes": f"API implementation using {api_tech} for {project_name}."
    }


def generate_frontend_task_from_requirements(project_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate frontend task based on project requirements."""
    project_name = project_context.get("project_name", "Project")
    tech_stack = project_context.get("tech_stack", [])

    frontend_tech = next((t for t in tech_stack if t.lower() in ['react', 'vue', 'angular', 'flutter']), 'modern frontend framework')

    return {
        "title": f"{project_name} - Frontend User Interface Development",
        "description": f"Develop the user interface for {project_name} using {frontend_tech}.",
        "acceptance_criteria": [
            "User interface is responsive and accessible",
            "All required features are implemented",
            "Application works across different devices",
            "Performance meets requirements"
        ],
        "technical_requirements": [
            f"Implement UI using {frontend_tech}",
            "Ensure responsive design",
            "Implement state management",
            "Optimize for performance"
        ],
        "implementation_steps": [
            "Set up frontend project structure",
            "Create UI components and layouts",
            "Implement application features",
            "Integrate with backend APIs",
            "Optimize and test"
        ],
        "subtasks": [
            f"Set up {frontend_tech} project",
            "Create component library",
            "Implement main application pages",
            "Set up routing and navigation",
            "Integrate API calls",
            "Implement form handling",
            "Add responsive design",
            "Optimize performance",
            "Add accessibility features",
            "Test across devices"
        ],
        "dependencies": ["Task 3: API Development and Integration"],
        "estimated_time": "3-4 weeks",
        "complexity": "High",
        "priority": "High",
        "deliverables": [
            "Complete frontend application",
            "Responsive user interface",
            "Component library",
            "Frontend documentation"
        ],
        "quality_gates": [
            "UI/UX review and approval",
            "Cross-device compatibility testing",
            "Performance testing",
            "Accessibility audit"
        ],
        "notes": f"Frontend implementation using {frontend_tech} for {project_name}."
    }


def generate_admin_task_from_requirements(project_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate admin panel task based on project requirements."""
    project_name = project_context.get("project_name", "Project")

    return {
        "title": f"{project_name} - Admin Panel and Management Interface",
        "description": f"Develop administrative interface for managing {project_name}.",
        "acceptance_criteria": [
            "Admin can manage all system entities",
            "User management is functional",
            "System configuration is accessible",
            "Analytics and reporting are available"
        ],
        "technical_requirements": [
            "Create admin dashboard interface",
            "Implement user management",
            "Add system configuration",
            "Create reporting and analytics"
        ],
        "implementation_steps": [
            "Design admin interface layout",
            "Implement user management features",
            "Create system configuration",
            "Add analytics and reporting",
            "Test admin functionality"
        ],
        "subtasks": [
            "Create admin dashboard layout",
            "Implement user management (CRUD)",
            "Add role and permission management",
            "Create system settings interface",
            "Implement data analytics",
            "Add reporting functionality",
            "Create audit logging",
            "Implement bulk operations",
            "Add data export features",
            "Test admin workflows"
        ],
        "dependencies": ["Task 2: Authentication and User Management"],
        "estimated_time": "2-3 weeks",
        "complexity": "Medium",
        "priority": "Medium",
        "deliverables": [
            "Admin dashboard",
            "User management interface",
            "System configuration",
            "Analytics and reporting"
        ],
        "quality_gates": [
            "Admin workflows tested",
            "User management functional",
            "Security review passed",
            "Performance acceptable"
        ],
        "notes": f"Administrative interface for {project_name} management."
    }


def generate_testing_task_from_requirements(project_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate testing task based on project requirements."""
    project_name = project_context.get("project_name", "Project")

    return {
        "title": f"{project_name} - Testing and Quality Assurance",
        "description": f"Implement comprehensive testing for {project_name}.",
        "acceptance_criteria": [
            "Test coverage meets requirements",
            "All critical features are tested",
            "Automated testing is functional",
            "Performance testing completed"
        ],
        "technical_requirements": [
            "Implement unit testing",
            "Create integration tests",
            "Set up end-to-end testing",
            "Perform performance testing"
        ],
        "implementation_steps": [
            "Set up testing framework",
            "Write unit tests",
            "Create integration tests",
            "Implement E2E testing",
            "Set up automated testing"
        ],
        "subtasks": [
            "Set up testing framework",
            "Write unit tests for core logic",
            "Create API integration tests",
            "Implement UI testing",
            "Set up automated test execution",
            "Create test data management",
            "Implement performance testing",
            "Add security testing",
            "Create test reporting",
            "Set up continuous testing"
        ],
        "dependencies": ["Task 4: Frontend User Interface Development"],
        "estimated_time": "2-3 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Test suite",
            "Automated testing pipeline",
            "Test coverage reports",
            "Performance test results"
        ],
        "quality_gates": [
            "Test coverage above 80%",
            "All tests passing",
            "Performance benchmarks met",
            "Security tests passed"
        ],
        "notes": f"Comprehensive testing strategy for {project_name}."
    }


def generate_deployment_task_from_requirements(project_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate deployment task based on project requirements."""
    project_name = project_context.get("project_name", "Project")
    tech_stack = project_context.get("tech_stack", [])

    cloud_tech = next((t for t in tech_stack if t.lower() in ['aws', 'azure', 'gcp', 'heroku']), 'cloud platform')

    return {
        "title": f"{project_name} - Production Deployment and DevOps",
        "description": f"Deploy {project_name} to production using {cloud_tech}.",
        "acceptance_criteria": [
            "Application deployed to production",
            "Monitoring and alerting operational",
            "Backup procedures in place",
            "Performance monitoring active"
        ],
        "technical_requirements": [
            f"Deploy to {cloud_tech}",
            "Set up monitoring and logging",
            "Configure backup procedures",
            "Implement security measures"
        ],
        "implementation_steps": [
            "Set up production environment",
            "Configure deployment pipeline",
            "Implement monitoring",
            "Set up backup procedures",
            "Deploy and validate"
        ],
        "subtasks": [
            f"Set up {cloud_tech} environment",
            "Configure production database",
            "Set up deployment pipeline",
            "Configure monitoring and alerting",
            "Set up log aggregation",
            "Implement backup procedures",
            "Configure security settings",
            "Set up SSL certificates",
            "Deploy application",
            "Validate production deployment"
        ],
        "dependencies": ["Task 6: Testing and Quality Assurance"],
        "estimated_time": "1-2 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Production deployment",
            "Monitoring system",
            "Backup procedures",
            "Deployment documentation"
        ],
        "quality_gates": [
            "Deployment successful",
            "Monitoring operational",
            "Backup tested",
            "Security validated"
        ],
        "notes": f"Production deployment of {project_name} on {cloud_tech}."
    }


def generate_authentication_task() -> Dict[str, Any]:
    """Generate authentication and user management task (legacy function)."""
    return {
        "title": "User Authentication and Authorization System",
        "description": "Implement comprehensive user authentication, authorization, and user management functionality.",
        "acceptance_criteria": [
            "Users can register, login, and logout securely",
            "Role-based access control is implemented",
            "Password security meets industry standards",
            "Session management is secure and efficient"
        ],
        "technical_requirements": [
            "Implement secure password hashing and storage",
            "Set up JWT or session-based authentication",
            "Create role-based permission system",
            "Implement password reset and email verification"
        ],
        "implementation_steps": [
            "Design user data models and database schema",
            "Implement user registration and login endpoints",
            "Set up password hashing and validation",
            "Create authentication middleware and guards",
            "Implement role-based access control"
        ],
        "subtasks": [
            "Create user model with proper validation",
            "Implement password hashing with bcrypt/argon2",
            "Set up JWT token generation and validation",
            "Create login/logout endpoints",
            "Implement user registration with email verification",
            "Set up password reset functionality",
            "Create role and permission models",
            "Implement authentication middleware",
            "Add rate limiting for auth endpoints"
        ],
        "dependencies": ["Task 2: Core Architecture and Database Design"],
        "estimated_time": "1-2 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "User authentication system",
            "Role-based access control",
            "Security documentation",
            "Authentication API endpoints"
        ],
        "quality_gates": [
            "Security audit and penetration testing",
            "Authentication flow testing",
            "Performance testing under load",
            "Code review focusing on security"
        ],
        "notes": "Security is paramount - follow OWASP guidelines and best practices."
    }


def generate_frontend_task(tech_stack: List[str]) -> Dict[str, Any]:
    """Generate frontend development task."""
    frontend_tech = "React" if "react" in str(tech_stack).lower() else "modern frontend framework"

    return {
        "title": "Frontend User Interface Development",
        "description": f"Develop the complete user interface using {frontend_tech} with responsive design and optimal user experience.",
        "acceptance_criteria": [
            "All UI components are responsive and accessible",
            "User interface matches design specifications",
            "Application works across different browsers and devices",
            "Performance metrics meet acceptable standards"
        ],
        "technical_requirements": [
            f"Implement UI using {frontend_tech}",
            "Ensure responsive design for mobile and desktop",
            "Implement state management and data flow",
            "Optimize for performance and accessibility"
        ],
        "implementation_steps": [
            "Set up frontend project structure and tooling",
            "Create reusable UI components and design system",
            "Implement main application pages and routing",
            "Integrate with backend APIs and handle data flow",
            "Optimize performance and add error handling"
        ],
        "subtasks": [
            "Set up component library and design system",
            "Create layout components (header, footer, navigation)",
            "Implement main application pages",
            "Set up routing and navigation",
            "Integrate API calls and data management",
            "Implement form handling and validation",
            "Add loading states and error handling",
            "Optimize bundle size and performance",
            "Implement responsive design breakpoints",
            "Add accessibility features (ARIA, keyboard navigation)"
        ],
        "dependencies": ["Task 2: Core Architecture and Database Design"],
        "estimated_time": "3-4 weeks",
        "complexity": "High",
        "priority": "High",
        "deliverables": [
            "Complete frontend application",
            "Component library and design system",
            "Responsive and accessible UI",
            "Frontend documentation"
        ],
        "quality_gates": [
            "Cross-browser compatibility testing",
            "Mobile responsiveness testing",
            "Accessibility audit (WCAG compliance)",
            "Performance testing and optimization"
        ],
        "notes": "Focus on user experience and accessibility throughout development."
    }


def generate_backend_task(tech_stack: List[str]) -> Dict[str, Any]:
    """Generate backend development task."""
    backend_tech = "FastAPI" if "fastapi" in str(tech_stack).lower() else "modern backend framework"

    return {
        "title": "Backend API and Business Logic Implementation",
        "description": f"Develop the complete backend system using {backend_tech} with robust API endpoints and business logic.",
        "acceptance_criteria": [
            "All API endpoints are functional and well-documented",
            "Business logic is properly implemented and tested",
            "Data validation and error handling are comprehensive",
            "API performance meets requirements"
        ],
        "technical_requirements": [
            f"Implement REST API using {backend_tech}",
            "Create comprehensive data validation",
            "Implement proper error handling and logging",
            "Ensure API security and rate limiting"
        ],
        "implementation_steps": [
            "Set up API framework and middleware",
            "Implement core business logic and services",
            "Create API endpoints with proper validation",
            "Add comprehensive error handling and logging",
            "Implement security measures and rate limiting"
        ],
        "subtasks": [
            "Set up API framework and project structure",
            "Implement data validation schemas",
            "Create CRUD operations for all entities",
            "Implement business logic and services",
            "Add comprehensive error handling",
            "Set up logging and monitoring",
            "Implement API rate limiting",
            "Add API documentation (OpenAPI/Swagger)",
            "Implement data serialization and pagination",
            "Add background task processing"
        ],
        "dependencies": ["Task 2: Core Architecture and Database Design"],
        "estimated_time": "3-4 weeks",
        "complexity": "High",
        "priority": "High",
        "deliverables": [
            "Complete backend API",
            "Business logic implementation",
            "API documentation",
            "Error handling and logging system"
        ],
        "quality_gates": [
            "API endpoint testing and validation",
            "Performance testing under load",
            "Security testing and audit",
            "Code review and quality assessment"
        ],
        "notes": "Ensure proper separation of concerns and maintainable code structure."
    }


def generate_agent_specific_tasks(agent_insights: Dict[str, str], project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate tasks based on specific agent analysis."""
    tasks = []

    # If we have agent insights, create tasks based on them
    if agent_insights:
        for agent_id, insight in agent_insights.items():
            if len(insight) > 100:  # Only create tasks for substantial insights
                task = {
                    "title": f"Implementation Based on {agent_id.replace('_', ' ').title()} Analysis",
                    "description": f"Implement recommendations and requirements identified by the {agent_id} agent analysis.",
                    "acceptance_criteria": [
                        "All recommendations from agent analysis are implemented",
                        "Implementation follows best practices identified",
                        "Quality standards meet agent specifications"
                    ],
                    "technical_requirements": [
                        "Follow architectural recommendations",
                        "Implement suggested technologies and patterns",
                        "Meet performance and quality criteria"
                    ],
                    "implementation_steps": [
                        "Review agent analysis and recommendations",
                        "Plan implementation approach",
                        "Implement core functionality",
                        "Test and validate implementation",
                        "Document implementation decisions"
                    ],
                    "subtasks": [
                        f"Review {agent_id} analysis in detail",
                        "Extract actionable recommendations",
                        "Plan implementation strategy",
                        "Implement recommended features",
                        "Validate against agent criteria"
                    ],
                    "dependencies": ["Task 2: Core Architecture and Database Design"],
                    "estimated_time": "1-2 weeks",
                    "complexity": "Medium",
                    "priority": "Medium",
                    "deliverables": [
                        "Implementation of agent recommendations",
                        "Documentation of implementation decisions",
                        "Test results and validation"
                    ],
                    "quality_gates": [
                        "Implementation review against agent analysis",
                        "Quality assurance testing",
                        "Performance validation"
                    ],
                    "notes": f"Based on analysis from {agent_id}: {insight[:200]}..."
                }
                tasks.append(task)

    return tasks


def generate_testing_task() -> Dict[str, Any]:
    """Generate comprehensive testing task."""
    return {
        "title": "Comprehensive Testing and Quality Assurance",
        "description": "Implement comprehensive testing strategy including unit tests, integration tests, and end-to-end testing.",
        "acceptance_criteria": [
            "Test coverage meets minimum requirements (80%+)",
            "All critical user journeys are tested",
            "Automated testing pipeline is functional",
            "Performance and security testing completed"
        ],
        "technical_requirements": [
            "Implement unit tests for all business logic",
            "Create integration tests for API endpoints",
            "Set up end-to-end testing for user workflows",
            "Implement performance and load testing"
        ],
        "implementation_steps": [
            "Set up testing framework and tools",
            "Write unit tests for core functionality",
            "Create integration tests for APIs",
            "Implement end-to-end testing scenarios",
            "Set up automated testing pipeline"
        ],
        "subtasks": [
            "Set up testing framework (Jest, Pytest, etc.)",
            "Write unit tests for business logic",
            "Create API integration tests",
            "Implement database testing with fixtures",
            "Set up end-to-end testing framework",
            "Create user journey test scenarios",
            "Implement performance testing",
            "Set up test data management",
            "Configure automated test execution",
            "Create test reporting and coverage analysis"
        ],
        "dependencies": ["Task 3: User Authentication", "Task 4: Frontend Development", "Task 5: Backend Development"],
        "estimated_time": "2-3 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Comprehensive test suite",
            "Automated testing pipeline",
            "Test coverage reports",
            "Performance testing results"
        ],
        "quality_gates": [
            "Minimum test coverage achieved",
            "All tests passing in CI/CD pipeline",
            "Performance benchmarks met",
            "Security testing completed"
        ],
        "notes": "Testing should be implemented throughout development, not just at the end."
    }


def generate_deployment_task() -> Dict[str, Any]:
    """Generate deployment and DevOps task."""
    return {
        "title": "Production Deployment and DevOps Setup",
        "description": "Set up production deployment pipeline, monitoring, and operational procedures for the application.",
        "acceptance_criteria": [
            "Application is successfully deployed to production",
            "Monitoring and alerting systems are operational",
            "Backup and disaster recovery procedures are in place",
            "Performance monitoring shows acceptable metrics"
        ],
        "technical_requirements": [
            "Set up production hosting environment",
            "Configure deployment automation",
            "Implement monitoring and logging",
            "Set up backup and recovery procedures"
        ],
        "implementation_steps": [
            "Configure production hosting environment",
            "Set up automated deployment pipeline",
            "Implement monitoring and alerting",
            "Configure backup and disaster recovery",
            "Perform production deployment and validation"
        ],
        "subtasks": [
            "Set up production hosting (cloud provider, VPS, etc.)",
            "Configure domain and SSL certificates",
            "Set up database in production environment",
            "Configure environment variables and secrets",
            "Set up automated deployment pipeline",
            "Implement application monitoring",
            "Set up log aggregation and analysis",
            "Configure alerting and notifications",
            "Set up automated backups",
            "Create disaster recovery procedures",
            "Perform production deployment",
            "Validate production functionality"
        ],
        "dependencies": ["Task 6: Comprehensive Testing"],
        "estimated_time": "1-2 weeks",
        "complexity": "Medium",
        "priority": "High",
        "deliverables": [
            "Production deployment",
            "Monitoring and alerting system",
            "Backup and recovery procedures",
            "Deployment documentation"
        ],
        "quality_gates": [
            "Production deployment successful",
            "All monitoring systems operational",
            "Backup procedures tested and verified",
            "Performance metrics within acceptable ranges"
        ],
        "notes": "Ensure proper security configurations and access controls in production."
    }


def generate_documentation_task() -> Dict[str, Any]:
    """Generate documentation and knowledge transfer task."""
    return {
        "title": "Documentation and Knowledge Transfer",
        "description": "Create comprehensive documentation for the project including technical documentation, user guides, and operational procedures.",
        "acceptance_criteria": [
            "All technical documentation is complete and accurate",
            "User documentation is clear and comprehensive",
            "Operational procedures are documented",
            "Knowledge transfer to stakeholders is completed"
        ],
        "technical_requirements": [
            "Create technical architecture documentation",
            "Write API documentation and guides",
            "Create user manuals and tutorials",
            "Document operational procedures"
        ],
        "implementation_steps": [
            "Create technical documentation structure",
            "Write comprehensive API documentation",
            "Create user guides and tutorials",
            "Document deployment and operational procedures",
            "Conduct knowledge transfer sessions"
        ],
        "subtasks": [
            "Create project README and overview",
            "Document system architecture and design decisions",
            "Write comprehensive API documentation",
            "Create database schema documentation",
            "Write user guides and tutorials",
            "Document installation and setup procedures",
            "Create troubleshooting guides",
            "Document backup and recovery procedures",
            "Create developer onboarding documentation",
            "Conduct knowledge transfer sessions"
        ],
        "dependencies": ["Task 7: Production Deployment"],
        "estimated_time": "1-2 weeks",
        "complexity": "Low",
        "priority": "Medium",
        "deliverables": [
            "Technical documentation",
            "User documentation",
            "Operational procedures",
            "Knowledge transfer completion"
        ],
        "quality_gates": [
            "Documentation review and approval",
            "User testing of documentation",
            "Knowledge transfer validation",
            "Documentation accessibility verification"
        ],
        "notes": "Good documentation is crucial for long-term project success and maintenance."
    }


def generate_tasks_index(project_name: str, task_definitions: List[Dict[str, Any]]) -> str:
    """Generate a tasks index file."""
    content = f"""# {project_name} - Tasks Index

## Overview
This document provides an overview of all project tasks and their relationships.

## Task Summary

| Task | Title | Priority | Estimated Time | Complexity |
|------|-------|----------|----------------|------------|
"""

    for i, task in enumerate(task_definitions, 1):
        content += f"| {i} | {task['title']} | {task['priority']} | {task['estimated_time']} | {task['complexity']} |\n"

    content += f"""

## Task Dependencies

```mermaid
graph TD
"""

    for i, task in enumerate(task_definitions, 1):
        task_id = f"T{i}"
        content += f"    {task_id}[\"{task['title']}\"]\n"

        for dep in task.get('dependencies', []):
            if dep.startswith('Task '):
                dep_num = dep.split(':')[0].replace('Task ', '')
                content += f"    T{dep_num} --> {task_id}\n"

    content += f"""```

## Phases

### Phase 1: Foundation (Tasks 1-2)
- Project setup and environment configuration
- Core architecture and database design

### Phase 2: Core Development (Tasks 3-5)
- Authentication and user management
- Frontend and backend implementation

### Phase 3: Quality Assurance (Task 6)
- Comprehensive testing and validation

### Phase 4: Deployment (Task 7)
- Production deployment and DevOps

### Phase 5: Documentation (Task 8)
- Documentation and knowledge transfer

## Total Estimated Time
**{sum([int(task['estimated_time'].split('-')[0]) for task in task_definitions if task['estimated_time'].split('-')[0].isdigit()])} - {sum([int(task['estimated_time'].split('-')[1].split()[0]) for task in task_definitions if '-' in task['estimated_time'] and task['estimated_time'].split('-')[1].split()[0].isdigit()])} weeks**

## Getting Started
1. Review all task files (Task1.md through Task{len(task_definitions)}.md)
2. Understand dependencies and sequencing
3. Assign tasks to team members based on skills and availability
4. Set up project tracking and monitoring
5. Begin with Task 1: Project Setup and Environment Configuration

---
*Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""

    return content



