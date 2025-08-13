# app/routes/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.core.securityDeps import get_current_user
from app.models.user import User
from app.models.userPatents import UserPatent
from app.models.patent import Patent
from app.schemas.dashboard import DashboardSummary, DashboardUserPatentItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user)])

@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = (current_user.role or "").lower()

    conds = []
    if role == "admin":
        pass
    elif role in ("viewer", "read_only", "leitor"):
        conds.append(UserPatent.tenant_id == current_user.tenant_id)
    else:
        conds.append(UserPatent.owner_id == current_user.id)

    # totais
    total_user_patents = db.query(func.count(UserPatent.id)).filter(*conds).scalar() or 0
    total_related_patents = (
        db.query(func.count(Patent.id))
        .join(UserPatent, Patent.user_patent_id == UserPatent.id)
        .filter(*conds)
        .scalar()
        or 0
    )

    # contagem por etapa
    rows = db.query(UserPatent.status, func.count(UserPatent.id)).filter(*conds).group_by(UserPatent.status).all()
    steps_counts = {int(s or 0): int(c or 0) for s, c in rows}
    for k in range(6):
        steps_counts.setdefault(k, 0)

    # top por relacionadas (no escopo)
    top_rows = (
        db.query(
            UserPatent.id,
            UserPatent.titulo,
            UserPatent.status,
            func.count(Patent.id).label("related_count"),
        )
        .outerjoin(Patent, Patent.user_patent_id == UserPatent.id)
        .filter(*conds)
        .group_by(UserPatent.id)
        .order_by(desc("related_count"), desc(UserPatent.id))
        .limit(10)
        .all()
    )

    top_user_patents = [
        DashboardUserPatentItem(id=r[0], titulo=r[1] or "", status=int(r[2] or 0), related_count=int(r[3] or 0))
        for r in top_rows
    ]

    return DashboardSummary(
        total_user_patents=int(total_user_patents),
        total_related_patents=int(total_related_patents),
        steps_counts=steps_counts,
        top_user_patents=top_user_patents,
    )
