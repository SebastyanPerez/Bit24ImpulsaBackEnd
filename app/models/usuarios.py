import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rol_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)
    nombre = Column(String(80), nullable=False)
    apellido = Column(String(80), nullable=False)
    correo = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    rol = relationship("Rol", back_populates="usuarios")
