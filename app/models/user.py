from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # multitenancy lógico (mesmo tenant agrupa usuários/recursos)
    tenant_id = Column(String, nullable=True, index=True)

    # nível de acesso
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
