import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ruta_id = Column(UUID(as_uuid=True), ForeignKey("rutas.id"), nullable=False)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    orden = Column(Integer, default=1, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    ruta = relationship("Ruta", back_populates="tareas")
    guias = relationship("Guia", back_populates="tarea")

