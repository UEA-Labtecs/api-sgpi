from pydantic import BaseModel
from typing import Optional, List, Dict

class PatentSchema(BaseModel):
    id: Optional[int] = None
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
    status: Optional[int] = 0
    info: Optional[Dict[int, dict]] = None

    class Config:
        from_attributes = True

class PatentCreateSchema(PatentSchema):
    pass

class EtapasUpdate(BaseModel):
    info: Dict[int, Dict[str, str]] 
    