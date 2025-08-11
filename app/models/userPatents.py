from sqlalchemy import JSON, Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.sql import text

class UserPatent(Base):
    __tablename__ = "user_patents"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    status = Column(Integer, nullable=False, default=1, server_default=text("1"))
    info = Column(JSON, nullable=True)

    patents = relationship("Patent", back_populates="user_patent", cascade="all, delete-orphan")
