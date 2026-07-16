import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class PreguntaIA(Base):
    __tablename__ = "preguntas_ia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    tarea_id = Column(UUID(as_uuid=True), ForeignKey("tareas.id"), nullable=True)
    guia_id = Column(UUID(as_uuid=True), ForeignKey("guias.id"), nullable=True)
    pregunta = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=True)
    categoria = Column(String(80), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    usuario = relationship("Usuario")
    tarea = relationship("Tarea")
    guia = relationship("Guia")
