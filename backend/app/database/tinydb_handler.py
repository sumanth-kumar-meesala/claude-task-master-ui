"""
TinyDB database handler for lightweight JSON-based storage.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import uuid

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import jsonschema
from jsonschema import validate, ValidationError

from app.core.config import get_settings
from app.core.exceptions import DatabaseException, ValidationException

logger = logging.getLogger(__name__)
settings = get_settings()


class TinyDBHandler:
    """Handler for TinyDB operations."""

    def __init__(self, db_path: str, schema: Optional[Dict[str, Any]] = None):
        """Initialize TinyDB handler."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.schema = schema

        # Initialize database with caching middleware and UTF-8 encoding
        self.db = TinyDB(
            self.db_path,
            storage=CachingMiddleware(JSONStorage),
            indent=2,
            ensure_ascii=True,  # Use ASCII encoding to avoid Unicode issues on Windows
            encoding='utf-8'
        )

        logger.info(f"TinyDB initialized at: {self.db_path}")
        if self.schema:
            logger.info(f"JSON schema validation enabled for {self.db_path}")

    def _validate_data(self, data: Dict[str, Any]) -> None:
        """Validate data against JSON schema if schema is provided."""
        if self.schema:
            try:
                validate(instance=data, schema=self.schema)
                logger.debug(f"Schema validation passed for data: {data.get('id', 'unknown')}")
            except ValidationError as e:
                logger.error(f"Schema validation failed for {data.get('id', 'unknown')}: {e.message}")
                logger.error(f"Failed data: {data}")
                raise ValidationException(f"Data validation failed: {e.message}")
            except Exception as e:
                logger.error(f"Unexpected validation error for {data.get('id', 'unknown')}: {e}")
                raise ValidationException(f"Validation error: {str(e)}")
        else:
            logger.debug("No schema validation (schema is None)")
    
    def insert(self, data: Dict[str, Any]) -> int:
        """Insert a document into the database."""
        try:
            logger.info(f"Attempting to insert document with ID: {data.get('id', 'unknown')}")

            # Validate data against schema
            self._validate_data(data)

            # Add metadata only if not already present
            if "created_at" not in data:
                data["created_at"] = datetime.utcnow().isoformat()
            if "updated_at" not in data:
                data["updated_at"] = datetime.utcnow().isoformat()

            if "id" not in data:
                data["id"] = str(uuid.uuid4())

            logger.info(f"Inserting document into database: {data.get('id')}")
            doc_id = self.db.insert(data)

            # Force flush to disk to ensure persistence
            if hasattr(self.db.storage, 'flush'):
                self.db.storage.flush()

            logger.info(f"Successfully inserted document with doc_id: {doc_id}, project_id: {data.get('id')}")
            return doc_id
        except ValidationException as e:
            logger.error(f"Validation failed for document {data.get('id', 'unknown')}: {e}")
            raise  # Re-raise validation exceptions
        except Exception as e:
            logger.error(f"Failed to insert document {data.get('id', 'unknown')}: {e}")
            raise DatabaseException(f"Failed to insert document: {str(e)}")
    
    def get_by_id(self, doc_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Get a document by its ID."""
        try:
            if isinstance(doc_id, str):
                # Search by custom ID field
                result = self.db.search(Query().id == doc_id)
                return result[0] if result else None
            else:
                # Search by TinyDB document ID
                return self.db.get(doc_id=doc_id)
        except Exception as e:
            logger.error(f"Failed to get document by ID {doc_id}: {e}")
            raise DatabaseException(f"Failed to get document: {str(e)}")
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all documents from the database."""
        try:
            return self.db.all()
        except Exception as e:
            logger.error(f"Failed to get all documents: {e}")
            raise DatabaseException(f"Failed to get documents: {str(e)}")
    
    def search(self, query: Query) -> List[Dict[str, Any]]:
        """Search documents using TinyDB query."""
        try:
            return self.db.search(query)
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise DatabaseException(f"Failed to search documents: {str(e)}")
    
    def update(self, doc_id: Union[str, int], data: Dict[str, Any]) -> bool:
        """Update a document by its ID."""
        try:
            # Get existing document for validation
            existing_doc = self.get_by_id(doc_id)
            if not existing_doc:
                return False

            # Merge with existing data for validation
            merged_data = {**existing_doc, **data}
            self._validate_data(merged_data)

            # Add update timestamp
            data["updated_at"] = datetime.utcnow().isoformat()

            if isinstance(doc_id, str):
                # Update by custom ID field
                updated = self.db.update(data, Query().id == doc_id)
            else:
                # Update by TinyDB document ID
                updated = self.db.update(data, doc_ids=[doc_id])

            success = len(updated) > 0
            if success:
                # Force flush to disk to ensure persistence
                if hasattr(self.db.storage, 'flush'):
                    self.db.storage.flush()
                logger.debug(f"Updated document with ID: {doc_id}")
            else:
                logger.warning(f"No document found with ID: {doc_id}")

            return success
        except ValidationException:
            raise  # Re-raise validation exceptions
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            raise DatabaseException(f"Failed to update document: {str(e)}")

    def update_by_id(self, doc_id: Union[str, int], data: Dict[str, Any]) -> bool:
        """Update a document by its ID. Alias for update method for compatibility."""
        return self.update(doc_id, data)
    
    def delete(self, doc_id: Union[str, int]) -> bool:
        """Delete a document by its ID."""
        try:
            if isinstance(doc_id, str):
                # Delete by custom ID field
                deleted = self.db.remove(Query().id == doc_id)
            else:
                # Delete by TinyDB document ID
                deleted = self.db.remove(doc_ids=[doc_id])
            
            success = len(deleted) > 0
            if success:
                logger.debug(f"Deleted document with ID: {doc_id}")
            else:
                logger.warning(f"No document found with ID: {doc_id}")
            
            return success
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            raise DatabaseException(f"Failed to delete document: {str(e)}")
    
    def count(self) -> int:
        """Get the total number of documents."""
        try:
            return len(self.db)
        except Exception as e:
            logger.error(f"Failed to count documents: {e}")
            raise DatabaseException(f"Failed to count documents: {str(e)}")
    
    def truncate(self) -> None:
        """Remove all documents from the database."""
        try:
            self.db.truncate()
            logger.info("Database truncated")
        except Exception as e:
            logger.error(f"Failed to truncate database: {e}")
            raise DatabaseException(f"Failed to truncate database: {str(e)}")

    def backup(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of the database.

        Args:
            backup_path: Optional custom backup path

        Returns:
            Path to the backup file
        """
        try:
            import shutil

            if backup_path is None:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{self.db_path.stem}_backup_{timestamp}.json"
                backup_path = self.db_path.parent / "backups" / backup_filename
            else:
                backup_path = Path(backup_path)

            # Create backup directory if it doesn't exist
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the database file
            shutil.copy2(self.db_path, backup_path)

            logger.info(f"Database backup created: {backup_path}")
            return str(backup_path)

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise DatabaseException(f"Backup failed: {str(e)}")

    def restore(self, backup_path: str) -> bool:
        """
        Restore database from backup.

        Args:
            backup_path: Path to the backup file

        Returns:
            True if restore was successful
        """
        try:
            import shutil

            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")

            # Close current database
            self.db.close()

            # Create a backup of current database before restore
            current_backup = self.backup(f"{self.db_path}.pre_restore_backup")
            logger.info(f"Current database backed up to: {current_backup}")

            # Restore from backup
            shutil.copy2(backup_file, self.db_path)

            # Reinitialize database
            self.db = TinyDB(
                self.db_path,
                storage=CachingMiddleware(JSONStorage),
                indent=2,
                ensure_ascii=False
            )

            logger.info(f"Database restored from: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            raise DatabaseException(f"Restore failed: {str(e)}")

    def get_backup_info(self) -> Dict[str, Any]:
        """
        Get information about available backups.

        Returns:
            Dictionary with backup information
        """
        try:
            backup_dir = self.db_path.parent / "backups"
            if not backup_dir.exists():
                return {"backup_directory": str(backup_dir), "backups": []}

            backups = []
            pattern = f"{self.db_path.stem}_backup_*.json"

            for backup_file in backup_dir.glob(pattern):
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

            # Sort by creation time, newest first
            backups.sort(key=lambda x: x["created_at"], reverse=True)

            return {
                "backup_directory": str(backup_dir),
                "total_backups": len(backups),
                "backups": backups
            }

        except Exception as e:
            logger.error(f"Failed to get backup info: {e}")
            return {"error": str(e)}

    def close(self) -> None:
        """Close the database connection."""
        try:
            self.db.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Failed to close database: {e}")


# Database instances
projects_db = None
templates_db = None
project_files_db = None
orchestration_sessions_db = None
collaboration_sessions_db = None
generated_files_db = None
project_structure_db = None
task_definitions_db = None


def get_projects_db() -> TinyDBHandler:
    """Get the projects database instance."""
    global projects_db
    if projects_db is None:
        from app.database.schemas import get_schema
        schema = get_schema("projects")
        projects_db = TinyDBHandler(settings.projects_db_path, schema)
    return projects_db





def get_templates_db() -> TinyDBHandler:
    """Get the templates database instance."""
    global templates_db
    if templates_db is None:
        from app.database.schemas import get_schema
        schema = get_schema("templates")
        templates_db = TinyDBHandler(settings.templates_db_path, schema)
    return templates_db


def get_project_files_db() -> TinyDBHandler:
    """Get the project files database instance."""
    global project_files_db
    if project_files_db is None:
        from app.database.schemas import get_schema
        schema = get_schema("project_files")
        project_files_db = TinyDBHandler(settings.project_files_db_path, schema)
    return project_files_db


def get_orchestration_sessions_db() -> TinyDBHandler:
    """Get the orchestration sessions database instance."""
    global orchestration_sessions_db
    if orchestration_sessions_db is None:
        from app.database.schemas import get_schema
        schema = get_schema("orchestration_sessions")
        orchestration_sessions_db = TinyDBHandler(settings.orchestration_sessions_db_path, schema)
    return orchestration_sessions_db


def get_collaboration_sessions_db() -> TinyDBHandler:
    """Get the collaboration sessions database instance."""
    global collaboration_sessions_db
    if collaboration_sessions_db is None:
        from app.database.schemas import get_schema
        schema = get_schema("collaboration_sessions")
        collaboration_sessions_db = TinyDBHandler(settings.collaboration_sessions_db_path, schema)
    return collaboration_sessions_db


def get_generated_files_db() -> TinyDBHandler:
    """Get the generated files database instance."""
    global generated_files_db
    if generated_files_db is None:
        from app.database.schemas import get_schema
        schema = get_schema("generated_files")
        generated_files_db = TinyDBHandler(settings.generated_files_db_path, schema)
    return generated_files_db


def get_project_structure_db() -> TinyDBHandler:
    """Get the project structure database instance."""
    global project_structure_db
    if project_structure_db is None:
        from app.database.schemas import get_schema
        schema = get_schema("project_structure")
        project_structure_db = TinyDBHandler(settings.project_structure_db_path, schema)
    return project_structure_db


def get_task_definitions_db() -> TinyDBHandler:
    """Get the task definitions database instance."""
    global task_definitions_db
    if task_definitions_db is None:
        from app.database.schemas import get_schema
        schema = get_schema("task_definitions")
        task_definitions_db = TinyDBHandler(settings.task_definitions_db_path, schema)
    return task_definitions_db


def initialize_database() -> None:
    """Initialize all database instances and create initial data files."""
    try:
        # Ensure data directory exists
        data_dir = Path(settings.TINYDB_PATH)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database files with empty arrays if they don't exist
        db_files = [
            settings.projects_db_path,
            settings.templates_db_path,
            settings.orchestration_sessions_db_path,
        ]
        
        for db_file in db_files:
            db_path = Path(db_file)
            if not db_path.exists():
                with open(db_path, 'w') as f:
                    json.dump({"_default": {}}, f, indent=2)
                logger.info(f"Created database file: {db_path}")
        
        # Initialize database instances
        get_projects_db()
        get_templates_db()
        get_orchestration_sessions_db()
        
        logger.info("All databases initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        raise DatabaseException(f"Database initialization failed: {str(e)}")


def close_all_databases() -> None:
    """Close all database connections."""
    global projects_db, templates_db, orchestration_sessions_db

    for db_instance in [projects_db, templates_db, orchestration_sessions_db]:
        if db_instance:
            db_instance.close()

    projects_db = None
    templates_db = None
    orchestration_sessions_db = None

    logger.info("All database connections closed")
