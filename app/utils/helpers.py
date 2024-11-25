from math import ceil
from typing import List, Type, TypeVar
from pydantic import BaseModel
from app.schemas.base import PaginatedResponse, PaginationMetadata

T = TypeVar("T", bound=BaseModel)

def convert_pydantic(data: dict, model: Type[T]) -> T:
    return model.model_validate(data)

def paginate(items: List[T], resp_type: T, total_items: int, current_page: int, items_per_page: int) -> PaginatedResponse[T]:
    total_pages = ceil(total_items / items_per_page)
    has_previous = current_page > 1
    has_next = current_page < total_pages

    meta_data = PaginationMetadata(
        total_items=total_items,
        items_per_page=items_per_page,
        current_page=current_page,
        total_pages=total_pages,
        has_previous=has_previous,
        has_next=has_next
    )

    items_pydantic = [convert_pydantic(item, resp_type) for item in items]
    return PaginatedResponse(
        items=items_pydantic,
        metadata=meta_data
    )
