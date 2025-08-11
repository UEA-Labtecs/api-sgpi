from pydantic import BaseModel, field_validator
from typing import Any, Optional, List, Dict

class PatentSchema(BaseModel):
    id: Optional[int] = None
    numero_pedido: Optional[str]  = None
    data_deposito: Optional[str] = None
    data_publicacao: Optional[str] = None
    data_concessao: Optional[str] = None
    classificacao_ipc: Optional[List[str]] = None
    classificacao_cpc: Optional[List[str]] = None
    titulo: Optional[str] = None
    resumo: Optional[str] = None
    depositante: Optional[str] = None
    inventores: Optional[str] = None
    url_detalhe: Optional[str] = None
    status: Optional[int] = 0
    info: Optional[Dict[int, dict]] = None
    
    @field_validator("classificacao_ipc", "classificacao_cpc", mode="before")
    @classmethod
    def normalize_classificacao(cls, v: Any):
        if v in (None, "", []):
            return None
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip() and str(x).strip() != "-"]
        if isinstance(v, dict):
            return [str(x).strip() for x in v.values() if str(x).strip() and str(x).strip() != "-"]
        if isinstance(v, str):
            parts = [p.strip() for p in re.split(r"[;,]", v) if p.strip()]
            return parts or None
        return None

    class Config:
        from_attributes = True
class PatentCreateSchema(PatentSchema):
    pass

class EtapasUpdate(BaseModel):
    info: Dict[int, Dict[str, str]]
    status: Optional[int] = None  