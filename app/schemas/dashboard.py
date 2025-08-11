from typing import Dict, List
from pydantic import BaseModel

class DashboardUserPatentItem(BaseModel):
    id: int
    titulo: str
    status: int
    related_count: int

class DashboardSummary(BaseModel):
    total_user_patents: int
    total_related_patents: int
    steps_counts: Dict[int, int]
    top_user_patents: List[DashboardUserPatentItem]
