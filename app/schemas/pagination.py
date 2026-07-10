from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    limit: int = Query(default=10, ge=1, le=100)
    offset: int = Query(default=0, ge=0)
