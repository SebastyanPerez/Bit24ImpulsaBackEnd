import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Actividad(Base):
    __tablename__ = "actividad"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    modulo = Column(String(80), nullable=False)
    accion = Column(String(100), nullable=False)
    referencia_id = Column(UUID(as_uuid=True), nullable=True)
    detalle = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    usuario = relationship("Usuario")
