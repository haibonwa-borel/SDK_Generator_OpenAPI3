from pydantic import BaseModel
from typing import List, Optional, Any

class User(BaseModel):
    id: int
    username: str
    email: str
    isActive: bool

class UserCreate(BaseModel):
    username: str
    email: str
    isActive: Optional[bool] = None

