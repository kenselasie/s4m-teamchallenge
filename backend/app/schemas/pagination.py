from typing import List, TypeVar, Generic
from pydantic import BaseModel, Field

# Generic type for paginated items
T = TypeVar("T")


class PaginationInfo(BaseModel):
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="List of items for current page")
    pagination: PaginationInfo = Field(..., description="Pagination metadata")


def create_paginated_response(
    items: List[T], page: int, size: int, total: int
) -> PaginatedResponse[T]:
    """Create a paginated response with calculated pagination info."""
    pages = (total + size - 1) // size if total > 0 else 0

    pagination_info = PaginationInfo(page=page, size=size, total=total, pages=pages)

    return PaginatedResponse(items=items, pagination=pagination_info)
