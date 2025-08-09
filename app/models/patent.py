from sqlalchemy import Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String, index=True)
    data_deposito = Column(String)
    data_publicacao = Column(String)
    data_concessao = Column(String)
    classificacao_ipc = Column(JSON)
    classificacao_cpc = Column(JSON)
    titulo = Column(String)
    resumo = Column(String)
    depositante = Column(String)
    inventores = Column(String)
    url_detalhe = Column(String)
    
    user_patent_id = Column(Integer, ForeignKey("user_patents.id"), nullable=True)
    user_patent = relationship("UserPatent", back_populates="patents")
