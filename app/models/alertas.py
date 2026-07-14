import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    titulo = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(String(50), nullable=True)
    canal = Column(String(20), default="Sistema", nullable=False)
    estado = Column(String(20), default="Pendiente", nullable=False)
    accion_recomendada = Column(Text, nullable=True)
    fecha_envio = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_atendida = Column(DateTime, nullable=True)

    usuario = relationship("Usuario")
