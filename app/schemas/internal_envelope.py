from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class InternalError(BaseModel):
    message: str
    code: str
    status_code: int
    request_id: str | None = None
    timestamp: str


class InternalResponse(BaseModel, Generic[T]):
    ok: bool
    data: T | None
    error: InternalError | None

