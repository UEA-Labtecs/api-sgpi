from typing import List, Optional, Dict
from pydantic import BaseModel

from app.schemas.patent import PatentSchema

class UserPatentCreate(BaseModel):
    titulo: str
    descricao: Optional[str]

class UserPatentSchema(UserPatentCreate):
    id: int
    status: int = 0
    info: Optional[Dict[int, Dict[str, str]]] = None
    patents: List[PatentSchema] = []

    class Config:
        from_attributes = True
