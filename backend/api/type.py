from typing import Generic, List, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    message: Optional[str] = None
    code: int = 200
    data: Optional[T]

class PageBody(BaseModel, Generic[T]):
    total: int
    list: List[T]
