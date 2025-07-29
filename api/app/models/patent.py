from sqlalchemy import Column, Integer, String, JSON
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
    status = Column(Integer, default=0)
    info = Column(JSON, nullable=True)
