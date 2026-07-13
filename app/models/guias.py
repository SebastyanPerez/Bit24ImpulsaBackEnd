import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Guia(Base):
    __tablename__ = "guias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tarea_id = Column(UUID(as_uuid=True), ForeignKey("tareas.id"), nullable=False)
    titulo = Column(String(100), nullable=False)
    contenido = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    duracion = Column(Integer, nullable=True)
    estado = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    tarea = relationship("Tarea", back_populates="guias")

