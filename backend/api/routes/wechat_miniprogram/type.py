from typing import Optional
from pydantic import BaseModel


class LLMRequestBody(BaseModel):
    type: str
    params: object


class ShareReq(BaseModel):
    type: str
    userId: int