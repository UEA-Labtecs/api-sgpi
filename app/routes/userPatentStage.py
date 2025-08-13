from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.securityDeps import get_current_user, require_write_access
from app.models.user import User
from app.models.userPatents import UserPatent
from app.models.userPatentStage import UserPatentStage
from app.schemas.userPatentStage import UserPatentStageOut
from app.services.storage_service import build_storage_from_app
from fastapi import Request

router = APIRouter(prefix="/patents/stages", tags=["Patent Stages"])
ALLOWED = {"application/pdf", "image/png", "image/jpeg"}
MAX_BYTES = 10 * 1024 * 1024
def ensure_access(db: Session, current_user: User, user_patent_id: int) -> UserPatent:
    role = (current_user.role or "").lower()
    q = db.query(UserPatent).filter(UserPatent.id == user_patent_id)
    if role in ("viewer", "read_only", "leitor", "admin"):
        pass
    else:
        q = q.filter(UserPatent.owner_id == current_user.id)
    obj = q.first()
    if not obj:
        raise HTTPException(status_code=404, detail="Patente não encontrada")
    return obj

@router.post("/{user_patent_id}", response_model=UserPatentStageOut, dependencies=[Depends(get_current_user), Depends(require_write_access)])
async def upsert_stage(
    user_patent_id: int,
    stage: int = Form(..., ge=3, le=6),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: User = Depends(get_current_user),
):
    ensure_access(db, current_user, user_patent_id)
    storage = build_storage_from_app(request.app)

    ups = db.query(UserPatentStage).filter(
        UserPatentStage.user_patent_id == user_patent_id,
        UserPatentStage.stage == stage
    ).first()

    new_key = None
    old_key = ups.file_key if ups else None

    if file:
        if file.content_type not in ALLOWED:
            raise HTTPException(status_code=415, detail="Tipo de arquivo não permitido")
        content = await file.read()
        if len(content) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="Arquivo muito grande")
        await file.seek(0)  
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        safe_name = (file.filename or "file").replace("/", "_").replace("\\", "_")
        new_key = f"patents/{user_patent_id}/stage-{stage}/{ts}-{safe_name}"

        # 1) faz upload do novo
        uploaded_key = await storage.upload(file, new_key)

        # 2) se havia antigo e é diferente, remove o antigo
        if old_key and old_key != uploaded_key:
            storage.delete(old_key)

    if ups:
        if description is not None:
            ups.description = description
        if new_key is not None:
            ups.file_key = new_key
    else:
        ups = UserPatentStage(
            user_patent_id=user_patent_id,
            stage=stage,
            description=description,
            file_key=new_key,
        )
        db.add(ups)

    db.commit()
    db.refresh(ups)

    url = storage.get_presigned_url(ups.file_key) if ups.file_key else None
    return {**UserPatentStageOut.model_validate(ups).model_dump(), "url": url}

@router.get("/{user_patent_id}/{stage}/url", dependencies=[Depends(get_current_user)])
def get_stage_file_url(
    user_patent_id: int,
    stage: int,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: User = Depends(get_current_user),
):
    ensure_access(db, current_user, user_patent_id)
    row = db.query(UserPatentStage).filter(
        UserPatentStage.user_patent_id == user_patent_id,
        UserPatentStage.stage == stage
    ).first()
    if not row or not row.file_key:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado para a etapa")
    storage = build_storage_from_app(request.app)
    return {"url": storage.get_presigned_url(row.file_key)}
