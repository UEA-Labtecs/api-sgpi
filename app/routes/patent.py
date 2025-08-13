from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.core.database import get_db
from app.core.securityDeps import get_current_user, same_tenant_or_404, require_write_access
from app.core.utils import _scope_user_patents_query
from app.models.user import User, UserRole
from app.models.userPatents import UserPatent
from app.models.patent import Patent
from app.schemas.patent import PatentSchema, PatentCreateSchema
from app.schemas.userPatents import UserPatentCreate, UserPatentSchema
from app.services import crawler_service

router = APIRouter(
    prefix="/patents",
    tags=["Patentes"],
    dependencies=[Depends(get_current_user)]  # 🔒 todo o router autenticado
)
@router.get("/search", response_model=List[PatentSchema], dependencies=[Depends(require_write_access)])
def buscar_patentes(
    termo: str = Query(...),
    quantidade: int = Query(1),
    user_patent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # se vier user_patent_id, valide ownership
    if user_patent_id is not None:
        same_tenant_or_404(db, current_user, user_patent_id)
    return crawler_service.run_crawler(db, termo, quantidade, user_patent_id)

@router.get("", response_model=List[UserPatentSchema])
def listar_patentes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(UserPatent)
    if current_user.role != UserRole.admin:
        q = q.filter(UserPatent.owner_id == current_user.id)
    return _scope_user_patents_query(db, current_user).all()

@router.get("/{patent_id}", response_model=UserPatentSchema)
def buscar_por_id(
    patent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = (
        _scope_user_patents_query(db, current_user)
        .options(joinedload(UserPatent.patents))
        .filter(UserPatent.id == patent_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Patente não encontrada")
    return obj

@router.post("/criar", response_model=PatentSchema, dependencies=[Depends(require_write_access)])
def criar_patente(
    patente: PatentCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # se o cliente informar user_patent_id, checar ownership
    if patente.user_patent_id is not None:
        same_tenant_or_404(db, current_user, patente.user_patent_id)

    db_patent = Patent(**patente.model_dump())
    db.add(db_patent)
    db.commit()
    db.refresh(db_patent)
    return db_patent

@router.put("/{patent_id}/etapas", response_model=UserPatentSchema, response_model_exclude_none=True, dependencies=[Depends(require_write_access)])
def atualizar_etapas(
    patent_id: int,
    payload: dict,  # ou seu schema {"status": int}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = _scope_user_patents_query(db, current_user).filter(UserPatent.id == patent_id)
    patent = q.first()
    if not patent:
        raise HTTPException(status_code=404, detail="Patente não encontrada")
    status = payload.get("status")
    patent.status = status if status is not None else (patent.status or 0) + 1
    db.commit()
    db.refresh(patent)
    return (
        db.query(UserPatent)
        .options(joinedload(UserPatent.patents))
        .filter(UserPatent.id == patent_id)
        .first()
    )

@router.post("/minhas-patentes", response_model=UserPatentSchema, dependencies=[Depends(require_write_access)])
def criar_user_patent(
    data: UserPatentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = UserPatent(
        titulo=data.titulo,
        descricao=data.descricao,
        owner_id=current_user.id,
        tenant_id=current_user.tenant_id,
        # status default + info None
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
