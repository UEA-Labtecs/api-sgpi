from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from typing import Dict, List
from app.schemas.patent import EtapasUpdate, PatentSchema, PatentCreateSchema
from app.models.patent import Patent
from app.services import crawler_service
from app.core.database import get_db

router = APIRouter(prefix="/patents", tags=["Patentes"])


@router.get("/search", response_model=List[PatentSchema])
def buscar_patentes(
    termo: str = Query(...),
    quantidade: int = Query(1),
    db: Session = Depends(get_db),
    # current_user=Depends(auth_service.get_current_user)
):
    return crawler_service.run_crawler(db, termo, quantidade)

@router.get("/", response_model=List[PatentSchema])
def listar_patentes(db: Session = Depends(get_db)):
    return db.query(Patent).all()

@router.get("/{patent_id}", response_model=PatentSchema)
def buscar_por_id(patent_id: int, db: Session = Depends(get_db)):
    patent = db.query(Patent).filter(Patent.id == patent_id).first()
    if not patent:
        raise HTTPException(status_code=404, detail="Patente não encontrada")
    return patent

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
    patent = db.query(Patent).filter(Patent.id == patent_id).first()
    if not patent:
        raise HTTPException(status_code=404, detail="Patente não encontrada")

    patent.status = data.status
    patent.info = data.info
    db.commit()
    db.refresh(patent)
    return {
        "id": patent.id,
        "titulo": patent.titulo,
        "numero_pedido": patent.numero_pedido,
        "status": patent.status,
        "info": patent.info,
    }