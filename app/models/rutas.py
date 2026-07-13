import uuid
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rol_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(Boolean, default=True, nullable=False)

    rol = relationship("Rol", back_populates="rutas")
    tareas = relationship("Tarea", back_populates="ruta")

