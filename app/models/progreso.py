import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Progreso(Base):
    __tablename__ = "progreso"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    tarea_id = Column(UUID(as_uuid=True), ForeignKey("tareas.id"), nullable=False)
    estado = Column(String(50), default="Pendiente", nullable=False)
    fecha_completado = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    usuario = relationship("Usuario")
    tarea = relationship("Tarea")
