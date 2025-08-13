from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, CheckConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class UserPatentStage(Base):
    __tablename__ = "user_patent_stages"
    __table_args__ = (
        UniqueConstraint("user_patent_id", "stage", name="uq_user_patent_stage"),
        CheckConstraint("stage BETWEEN 3 AND 6", name="ck_stage_range_3_6"),
    )

    id = Column(Integer, primary_key=True)
    user_patent_id = Column(Integer, ForeignKey("user_patents.id", ondelete="CASCADE"), index=True, nullable=False)
    stage = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    file_key = Column(String, nullable=True)
    uploaded_at = Column(DateTime, server_default=func.now(), nullable=False)

    user_patent = relationship("UserPatent")
