"""
Base classes for API operations and CRUD functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from fastapi import HTTPException, status
from pydantic import BaseModel
import logging

from app.database.tinydb_handler import TinyDBHandler
from app.core.exceptions import DatabaseException, ValidationException

logger = logging.getLogger(__name__)

# Type variables for generic CRUD operations
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """
    Base class for CRUD operations with TinyDB.
    
    This class provides common CRUD operations that can be inherited
    by specific resource handlers.
    """
    
    def __init__(self, db_handler: TinyDBHandler, model: Type[ModelType]):
        """
        Initialize CRUD base class.
        
        Args:
            db_handler: TinyDB handler instance
            model: Pydantic model class for data validation
        """
        self.db = db_handler
        self.model = model
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            obj_in: Input data for creating the record
            
        Returns:
            Created record as model instance
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            # Convert Pydantic model to dict
            obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
            
            # Insert into database
            doc_id = self.db.insert(obj_data)
            
            # Retrieve the created record
            created_record = self.db.get_by_id(doc_id)
            if not created_record:
                raise DatabaseException("Failed to retrieve created record")
            
            # Return as model instance
            return self.model(**created_record)
            
        except DatabaseException as e:
            logger.error(f"Database error during create: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create record: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during create: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get(self, id: str) -> Optional[ModelType]:
        """
        Get a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Record as model instance or None if not found
        """
        try:
            record = self.db.get_by_id(id)
            if record:
                return self.model(**record)
            return None
            
        except Exception as e:
            logger.error(f"Error getting record {id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve record"
            )
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of records as model instances
        """
        try:
            all_records = self.db.get_all()
            
            # Apply pagination
            paginated_records = all_records[skip:skip + limit]
            
            # Convert to model instances
            return [self.model(**record) for record in paginated_records]
            
        except Exception as e:
            logger.error(f"Error getting multiple records: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve records"
            )
    
    async def update(self, id: str, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """
        Update a record by ID.
        
        Args:
            id: Record ID
            obj_in: Update data
            
        Returns:
            Updated record as model instance or None if not found
        """
        try:
            # Check if record exists
            existing_record = await self.get(id)
            if not existing_record:
                return None
            
            # Convert update data to dict
            update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
            
            # Update in database
            success = self.db.update(id, update_data)
            if not success:
                raise DatabaseException("Failed to update record")
            
            # Return updated record
            return await self.get(id)
            
        except DatabaseException as e:
            logger.error(f"Database error during update: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update record: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during update: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def delete(self, id: str) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Check if record exists
            existing_record = await self.get(id)
            if not existing_record:
                return False
            
            # Delete from database
            success = self.db.delete(id)
            return success
            
        except Exception as e:
            logger.error(f"Error deleting record {id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete record"
            )
    
    async def count(self) -> int:
        """
        Get total count of records.
        
        Returns:
            Total number of records
        """
        try:
            all_records = self.db.get_all()
            return len(all_records)
            
        except Exception as e:
            logger.error(f"Error counting records: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to count records"
            )


class BaseAPIRouter(ABC):
    """
    Base class for API routers with common functionality.
    """
    
    def __init__(self, crud: BaseCRUD, prefix: str, tags: List[str]):
        """
        Initialize base API router.
        
        Args:
            crud: CRUD operations handler
            prefix: URL prefix for the router
            tags: OpenAPI tags for documentation
        """
        self.crud = crud
        self.prefix = prefix
        self.tags = tags
    
    @abstractmethod
    def get_router(self):
        """
        Get the FastAPI router instance.
        
        Returns:
            FastAPI APIRouter instance
        """
        pass


class PaginationParams(BaseModel):
    """
    Standard pagination parameters.
    """
    skip: int = 0
    limit: int = 100
    
    class Config:
        json_schema_extra = {
            "example": {
                "skip": 0,
                "limit": 100
            }
        }


class SearchParams(BaseModel):
    """
    Standard search parameters.
    """
    query: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: str = "asc"
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "search term",
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }
