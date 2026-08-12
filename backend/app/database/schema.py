import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.database.connection import Base


class Document(Base):
    """SQLAlchemy model representing document ingestion metadata and statuses."""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    document_type = Column(String, nullable=False)  # company_policy, regulation, contract, sop
    document_version = Column(String, nullable=False, default="1.0.0")
    file_path = Column(String, nullable=False)
    chunk_count = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False, default="processing")  # processing, indexed, failed
