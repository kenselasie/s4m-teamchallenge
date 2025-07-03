"""
Base repository class with common CRUD operations.
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from ..models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get(self, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        query = self.db.query(self.model)
        
        if order_by:
            order_column = getattr(self.model, order_by, None)
            if order_column:
                query = query.order_by(desc(order_column) if order_desc else asc(order_column))
        
        return query.offset(skip).limit(limit).all()
    
    def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record."""
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> Optional[ModelType]:
        """Delete a record."""
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        self.db.delete(db_obj)
        self.db.commit()
        return db_obj
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters."""
        query = self.db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.count()
    
    def exists(self, id: int) -> bool:
        """Check if record exists."""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
    
    def filter_by(self, **kwargs) -> List[ModelType]:
        """Filter records by field values."""
        return self.db.query(self.model).filter_by(**kwargs).all()
    
    def search(self, search_term: str, search_fields: List[str]) -> List[ModelType]:
        """Search records across multiple fields."""
        if not search_term or not search_fields:
            return []
        
        conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                field_attr = getattr(self.model, field)
                conditions.append(field_attr.ilike(f"%{search_term}%"))
        
        if not conditions:
            return []
        
        return self.db.query(self.model).filter(or_(*conditions)).all()