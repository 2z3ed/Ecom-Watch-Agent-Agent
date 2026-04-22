from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class CandidateBatch(Base):
    __tablename__ = "candidate_batches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    query: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="discovery")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    items = relationship("CandidateItem", back_populates="batch", cascade="all, delete-orphan")
