"""
Prompt management for AI agents.
"""

from .prompt_manager import PromptManager, get_prompt_manager
from .agent_prompts import AGENT_PROMPTS, TASK_PROMPTS, AGENT_CONFIGS

__all__ = [
    "PromptManager",
    "get_prompt_manager",
    "AGENT_PROMPTS",
    "TASK_PROMPTS",
    "AGENT_CONFIGS",
]
