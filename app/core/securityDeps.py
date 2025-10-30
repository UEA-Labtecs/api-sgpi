# app/core/security_deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token  # seu decoder JWT
from app.models.user import User, UserRole

security = HTTPBearer(auto_error=True)  # força 401 se não houver Authorization

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    # garante esquema Bearer
    if (credentials.scheme or "").lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth scheme")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)  # deve conter {"sub": email}
        email = payload.get("sub")
        if not email:
            raise ValueError("sub missing")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user

def same_tenant_or_404(db: Session, user: User, user_patent_id: int):
    from app.models.userPatents import UserPatent
    q = db.query(UserPatent).filter(UserPatent.id == user_patent_id)
    if user.role != UserRole.admin:
        q = q.filter(UserPatent.owner_id == user.id)  # escopo por dono
    obj = q.first()
    if not obj:
        raise HTTPException(status_code=404, detail="Patente não encontrada")
    return obj

def require_roles(*allowed):
    def _dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current_user
    return _dep

def require_write_access(current_user: User = Depends(get_current_user)) -> User:
    # bloqueia quem é somente leitura
    if current_user.role == UserRole.viewer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conta somente leitura")
    return current_user
