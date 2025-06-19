"""
Application configuration using Pydantic settings.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings."""
    
    # Basic app settings
    APP_NAME: str = "Project Overview Agent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS settings
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174",
        env="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: str = Field(
        default="localhost,127.0.0.1,0.0.0.0",
        env="ALLOWED_HOSTS"
    )
    
    # Database settings
    TINYDB_PATH: str = Field(default="../data", env="TINYDB_PATH")
    
    # AI/LLM settings
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash-preview-05-20", env="GEMINI_MODEL")
    GEMINI_TEMPERATURE: float = Field(default=0.7, env="GEMINI_TEMPERATURE")
    GEMINI_MAX_TOKENS: int = Field(default=2048, env="GEMINI_MAX_TOKENS")
    
    # CrewAI settings
    CREWAI_LOG_LEVEL: str = Field(default="INFO", env="CREWAI_LOG_LEVEL")
    CREWAI_VERBOSE: bool = Field(default=True, env="CREWAI_VERBOSE")
    CREWAI_MEMORY: bool = Field(default=False, env="CREWAI_MEMORY")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    MAX_REQUEST_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_REQUEST_SIZE")  # 10MB
    REQUEST_TIMEOUT: int = Field(default=300, env="REQUEST_TIMEOUT")  # 5 minutes
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as a list."""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]

    @field_validator("TINYDB_PATH")
    @classmethod
    def validate_tinydb_path(cls, v):
        """Ensure TinyDB path exists."""
        path = Path(v)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return str(path.absolute())

    @field_validator("GEMINI_API_KEY")
    @classmethod
    def validate_gemini_api_key(cls, v):
        """Validate Gemini API key is provided."""
        # Temporarily disabled for testing - allow placeholder values
        if not v and not os.getenv("TESTING"):
            logger.warning("GEMINI_API_KEY not set - some features may not work")
        return v
    
    @property
    def database_url(self) -> str:
        """Get database URL for TinyDB."""
        return str(Path(self.TINYDB_PATH) / "main.json")
    
    @property
    def projects_db_path(self) -> str:
        """Get projects database path."""
        return str(Path(self.TINYDB_PATH) / "projects.json")
    

    
    @property
    def templates_db_path(self) -> str:
        """Get templates database path."""
        return str(Path(self.TINYDB_PATH) / "templates.json")

    @property
    def project_files_db_path(self) -> str:
        """Get project files database path."""
        return str(Path(self.TINYDB_PATH) / "project_files.json")

    @property
    def orchestration_sessions_db_path(self) -> str:
        """Get orchestration sessions database path."""
        return str(Path(self.TINYDB_PATH) / "orchestration_sessions.json")

    @property
    def collaboration_sessions_db_path(self) -> str:
        """Get collaboration sessions database path."""
        return str(Path(self.TINYDB_PATH) / "collaboration_sessions.json")

    @property
    def generated_files_db_path(self) -> str:
        """Get generated files database path."""
        return str(Path(self.TINYDB_PATH) / "generated_files.json")

    @property
    def project_structure_db_path(self) -> str:
        """Get project structure database path."""
        return str(Path(self.TINYDB_PATH) / "project_structure.json")

    @property
    def task_definitions_db_path(self) -> str:
        """Get task definitions database path."""
        return str(Path(self.TINYDB_PATH) / "task_definitions.json")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }


class DevelopmentSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    CREWAI_VERBOSE: bool = True


class ProductionSettings(Settings):
    """Production environment settings."""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CREWAI_VERBOSE: bool = False


class TestingSettings(Settings):
    """Testing environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    TINYDB_PATH: str = "./test_data"
    GEMINI_API_KEY: str = "test-key"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings based on environment."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
