from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.schemas.patent import PatentSchema
from app.services import auth_service, crawler_service
from app.core.database import get_db

router = APIRouter(prefix="/patentes", tags=["Patentes"])

@router.get("/", response_model=List[PatentSchema])
def buscar_patentes(
    termo: str = Query(...),
    quantidade: int = Query(1),
    db: Session = Depends(get_db),
    # current_user=Depends(auth_service.get_current_user)
):
    return crawler_service.run_crawler(db, termo, quantidade)
