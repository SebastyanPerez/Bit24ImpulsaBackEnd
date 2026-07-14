import uuid
from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy.sql import func
from app.database import Base

class CategoriaSoporte(Base):
    __tablename__ = "categorias_soporte"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
