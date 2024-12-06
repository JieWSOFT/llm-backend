from typing import Generic, TypeVar,Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel,Generic[T]):
    message: Optional[str] = None
    code: int
    data: T