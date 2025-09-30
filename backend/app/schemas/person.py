from pydantic import BaseModel
from typing import Optional


class PersonCreate(BaseModel):
    name: str
    note: Optional[str] = None


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    note: Optional[str] = None


class PersonOut(BaseModel):
    id: int
    name: str
    note: Optional[str] = None