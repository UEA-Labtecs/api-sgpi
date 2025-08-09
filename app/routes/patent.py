from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from typing import Dict, List, Optional
from app.models.userPatents import UserPatent
from app.schemas.patent import EtapasUpdate, PatentSchema, PatentCreateSchema
from app.models.patent import Patent
from app.schemas.userPatents import UserPatentCreate, UserPatentSchema
from app.services import crawler_service
from app.core.database import get_db
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/patents", tags=["Patentes"])


@router.get("/search", response_model=List[PatentSchema])
def buscar_patentes(
    termo: str = Query(...),
    quantidade: int = Query(1),
    user_patent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return crawler_service.run_crawler(db, termo, quantidade, user_patent_id)

@router.get("", response_model=List[PatentSchema])
def listar_patentes(db: Session = Depends(get_db)):
    return db.query(Patent).all()

@router.get("/{patent_id}", response_model=UserPatentSchema)
def buscar_por_id(patent_id: int, db: Session = Depends(get_db)):
    user_patent = (
        db.query(UserPatent)
        .options(joinedload(UserPatent.patents))
        .filter(UserPatent.id == patent_id)
        .first()
    )
    if not user_patent:
        raise HTTPException(status_code=404, detail="Patente não encontrada")
    return user_patent

@router.post("/criar", response_model=PatentSchema)
def criar_patente(patente: PatentCreateSchema, db: Session = Depends(get_db)):
    db_patent = Patent(**patente.dict())
    db.add(db_patent)
    db.commit()
    db.refresh(db_patent)
    return db_patent

@router.put("/{patent_id}/etapas", response_model=dict)
def atualizar_etapas(
    patent_id: int,
    data: EtapasUpdate = ...,
    db: Session = Depends(get_db)
):
    patent = db.query(UserPatent).filter(UserPatent.id == patent_id).first()
    if not patent:
        raise HTTPException(status_code=404, detail="Patente não encontrada")

    patent.status = data.info.__len__()
    patent.info = data.info
    db.commit()
    db.refresh(patent)
    return {
        "id": patent.id,
        "titulo": patent.titulo,
        "status": patent.status,
        "info": patent.info,
    }
    

@router.post("/minhas-patentes", response_model=UserPatentSchema)
def criar_user_patent(data: UserPatentCreate, db: Session = Depends(get_db)):
    obj = UserPatent(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
