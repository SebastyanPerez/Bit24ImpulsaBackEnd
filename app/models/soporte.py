import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Soporte(Base):
    __tablename__ = "soporte"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias_soporte.id"), nullable=False)
    responsable_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(String(30), default="pendiente", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    categoria = relationship("CategoriaSoporte")
    responsable = relationship("Usuario", foreign_keys=[responsable_id])
