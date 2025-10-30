from pydantic import BaseModel, constr
from typing import Optional
from app.models.user import UserRole

class UserCreate(BaseModel):
    name: str
    email: str
    # bcrypt aceita no máximo 72 bytes; limitar para evitar 500
    password: constr(min_length=8, max_length=72)  # type: ignore[valid-type]
    tenant_id: Optional[str] = None
    role: Optional[UserRole] = None  # opcional para seeding/admin inicial

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"