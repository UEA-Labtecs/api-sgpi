from pydantic import BaseModel, Field
from typing import Optional

class UserPatentStageCreate(BaseModel):
    stage: int = Field(ge=3, le=6)
    description: Optional[str] = None

class UserPatentStageOut(BaseModel):
    id: int
    user_patent_id: int
    stage: int
    description: Optional[str] = None
    file_key: Optional[str] = None

    class Config:
        from_attributes = True
