from typing import List, Optional, Dict
from pydantic import BaseModel
from app.schemas.patent import PatentSchema

class UserPatentCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None

class UserPatentSchema(UserPatentCreate):
    id: int
    status: int = 0
    info: Optional[Dict[int, Dict[str, str]]] = None
    patents: List[PatentSchema] = []
    # opcional:
    # owner_id: int
    # tenant_id: Optional[str] = None

    class Config:
        from_attributes = True
