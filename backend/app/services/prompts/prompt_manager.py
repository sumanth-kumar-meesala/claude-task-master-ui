"""
Prompt management system for AI agents.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import yaml
from datetime import datetime

from app.core.config import get_settings
from app.core.exceptions import ConfigurationException

logger = logging.getLogger(__name__)
settings = get_settings()


class PromptManager:
    """
    Manages prompts for AI agents and tasks.
    
    Supports loading prompts from files, templates, and dynamic generation.
    """
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize prompt manager.
        
        Args:
            prompts_dir: Directory containing prompt files
        """
        self.prompts_dir = Path(prompts_dir) if prompts_dir else Path("prompts")
        self.prompts_cache: Dict[str, Dict[str, Any]] = {}
        self.templates_cache: Dict[str, str] = {}
        
        # Ensure prompts directory exists
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Load prompts from files
        self._load_prompts()
        
        logger.info(f"PromptManager initialized with directory: {self.prompts_dir}")
    
    def _load_prompts(self) -> None:
        """Load prompts from files in the prompts directory."""
        try:
            # Load YAML prompt files
            for yaml_file in self.prompts_dir.glob("*.yaml"):
                self._load_yaml_file(yaml_file)
            
            for yml_file in self.prompts_dir.glob("*.yml"):
                self._load_yaml_file(yml_file)
            
            # Load JSON prompt files
            for json_file in self.prompts_dir.glob("*.json"):
                self._load_json_file(json_file)
            
            # Load text template files
            for txt_file in self.prompts_dir.glob("*.txt"):
                self._load_text_file(txt_file)
            
            logger.info(f"Loaded {len(self.prompts_cache)} prompt categories")
            
        except Exception as e:
            logger.error(f"Failed to load prompts: {e}")
            raise ConfigurationException(f"Prompt loading failed: {str(e)}")
    
    def _load_yaml_file(self, file_path: Path) -> None:
        """Load prompts from a YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            category = file_path.stem
            self.prompts_cache[category] = data
            logger.debug(f"Loaded YAML prompts from: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {e}")
    
    def _load_json_file(self, file_path: Path) -> None:
        """Load prompts from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            category = file_path.stem
            self.prompts_cache[category] = data
            logger.debug(f"Loaded JSON prompts from: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {e}")
    
    def _load_text_file(self, file_path: Path) -> None:
        """Load template from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            template_name = file_path.stem
            self.templates_cache[template_name] = content
            logger.debug(f"Loaded text template from: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load text file {file_path}: {e}")
    
    def get_prompt(self, category: str, prompt_name: str, **kwargs) -> str:
        """
        Get a prompt by category and name.
        
        Args:
            category: Prompt category
            prompt_name: Prompt name within the category
            **kwargs: Variables to substitute in the prompt
            
        Returns:
            Formatted prompt string
            
        Raises:
            ConfigurationException: If prompt not found
        """
        try:
            if category not in self.prompts_cache:
                raise ConfigurationException(f"Prompt category '{category}' not found")
            
            category_prompts = self.prompts_cache[category]
            
            if prompt_name not in category_prompts:
                raise ConfigurationException(f"Prompt '{prompt_name}' not found in category '{category}'")
            
            prompt_data = category_prompts[prompt_name]
            
            # Handle different prompt formats
            if isinstance(prompt_data, str):
                prompt_text = prompt_data
            elif isinstance(prompt_data, dict):
                prompt_text = prompt_data.get('text', prompt_data.get('prompt', ''))
                
                # Apply any default variables
                defaults = prompt_data.get('defaults', {})
                kwargs = {**defaults, **kwargs}
            else:
                raise ConfigurationException(f"Invalid prompt format for '{category}.{prompt_name}'")
            
            # Format the prompt with provided variables
            return self._format_prompt(prompt_text, **kwargs)
            
        except Exception as e:
            logger.error(f"Failed to get prompt {category}.{prompt_name}: {e}")
            raise ConfigurationException(f"Prompt retrieval failed: {str(e)}")
    
    def get_template(self, template_name: str, **kwargs) -> str:
        """
        Get a template by name.
        
        Args:
            template_name: Template name
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted template string
        """
        try:
            if template_name not in self.templates_cache:
                raise ConfigurationException(f"Template '{template_name}' not found")
            
            template_text = self.templates_cache[template_name]
            return self._format_prompt(template_text, **kwargs)
            
        except Exception as e:
            logger.error(f"Failed to get template {template_name}: {e}")
            raise ConfigurationException(f"Template retrieval failed: {str(e)}")
    
    def _format_prompt(self, prompt_text: str, **kwargs) -> str:
        """
        Format a prompt with variables.
        
        Args:
            prompt_text: Raw prompt text
            **kwargs: Variables to substitute
            
        Returns:
            Formatted prompt
        """
        try:
            # Add common variables
            common_vars = {
                'timestamp': datetime.utcnow().isoformat(),
                'date': datetime.utcnow().strftime('%Y-%m-%d'),
                'time': datetime.utcnow().strftime('%H:%M:%S'),
            }
            
            # Merge variables
            all_vars = {**common_vars, **kwargs}
            
            # Format the prompt
            return prompt_text.format(**all_vars)
            
        except KeyError as e:
            logger.error(f"Missing variable in prompt: {e}")
            raise ConfigurationException(f"Missing prompt variable: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to format prompt: {e}")
            raise ConfigurationException(f"Prompt formatting failed: {str(e)}")
    
    def list_categories(self) -> List[str]:
        """Get list of available prompt categories."""
        return list(self.prompts_cache.keys())
    
    def list_prompts(self, category: str) -> List[str]:
        """Get list of prompts in a category."""
        if category not in self.prompts_cache:
            return []
        return list(self.prompts_cache[category].keys())
    
    def list_templates(self) -> List[str]:
        """Get list of available templates."""
        return list(self.templates_cache.keys())
    
    def reload_prompts(self) -> None:
        """Reload all prompts from files."""
        self.prompts_cache.clear()
        self.templates_cache.clear()
        self._load_prompts()
        logger.info("Prompts reloaded")
    
    def add_prompt(self, category: str, prompt_name: str, prompt_text: str, **metadata) -> None:
        """
        Add a prompt programmatically.
        
        Args:
            category: Prompt category
            prompt_name: Prompt name
            prompt_text: Prompt text
            **metadata: Additional metadata
        """
        if category not in self.prompts_cache:
            self.prompts_cache[category] = {}
        
        prompt_data = {
            'text': prompt_text,
            'added_at': datetime.utcnow().isoformat(),
            **metadata
        }
        
        self.prompts_cache[category][prompt_name] = prompt_data
        logger.info(f"Added prompt: {category}.{prompt_name}")
    
    def get_prompt_info(self, category: str, prompt_name: str) -> Dict[str, Any]:
        """
        Get metadata about a prompt.
        
        Args:
            category: Prompt category
            prompt_name: Prompt name
            
        Returns:
            Prompt metadata
        """
        if category not in self.prompts_cache:
            return {}
        
        if prompt_name not in self.prompts_cache[category]:
            return {}
        
        prompt_data = self.prompts_cache[category][prompt_name]
        
        if isinstance(prompt_data, dict):
            return {k: v for k, v in prompt_data.items() if k != 'text'}
        
        return {}


# Global prompt manager instance
_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """Get the global prompt manager instance."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager
