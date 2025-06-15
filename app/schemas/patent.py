from pydantic import BaseModel
from typing import Optional, List

class PatentSchema(BaseModel):
    numero_pedido: Optional[str]
    data_deposito: Optional[str]
    data_publicacao: Optional[str]
    data_concessao: Optional[str]
    classificacao_ipc: Optional[List[str]]
    classificacao_cpc: Optional[List[str]]
    titulo: Optional[str]
    resumo: Optional[str]
    depositante: Optional[str]
    inventores: Optional[str]
    url_detalhe: Optional[str]

    class Config:
        orm_mode = True
