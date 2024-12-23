from typing import Optional
from pydantic import BaseModel


class llmTempBody(BaseModel):
    id: Optional[int] = None
    type: str
    template: str
