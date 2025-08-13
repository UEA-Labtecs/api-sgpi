from pydantic import BaseModel
from typing import Optional
from app.models.user import UserRole

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    tenant_id: Optional[str] = None
    role: Optional[UserRole] = None  # opcional para seeding/admin inicial

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"