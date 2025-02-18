from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import DEFAULT_LIMIT, DEFAULT_SKIP, MAX_LIMIT

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Base pagination parameters schema."""
    skip: int = Field(
        default=DEFAULT_SKIP,
        ge=0,
        description="Number of records to skip"
    )
    limit: int = Field(
        default=DEFAULT_LIMIT,
        ge=1,
        le=MAX_LIMIT,
        description="Maximum number of records to return"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "skip": 0,
                "limit": 20
            }
        }
    )

class PaginatedList(BaseModel, Generic[T]):
    """Generic schema for paginated lists."""
    items: Sequence[T]
    total: int = Field(description="Total number of records available")
    skip: int = Field(description="Number of records skipped")
    limit: int = Field(description="Maximum number of records per page")
    page: int = Field(description="Current page number")
    pages: int = Field(description="Total number of pages")
    per_page: int = Field(description="Number of items per page")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "items": [],
                "total": 100,
                "skip": 0,
                "limit": 20,
                "page": 1,
                "pages": 5,
                "per_page": 20,
                "has_next": True,
                "has_prev": False
            }
        }
    )
