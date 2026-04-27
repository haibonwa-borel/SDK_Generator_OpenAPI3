from pydantic import BaseModel
from typing import List, Optional, Any

class Pet(BaseModel):
    id: int
    name: str
    tag: Optional[str] = None

class Pets(BaseModel):
    pass

class Error(BaseModel):
    code: int
    message: str

