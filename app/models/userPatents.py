from sqlalchemy import JSON, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.sql import text

class UserPatent(Base):
    __tablename__ = "user_patents"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    status = Column(Integer, nullable=False, default=1, server_default=text("1"))
    
    # multitenancy + ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(String, nullable=True, index=True)

    owner = relationship("User")  # opcional: back_populates se quiser

    patents = relationship("Patent", back_populates="user_patent", cascade="all, delete-orphan")
