import uuid
from sqlalchemy import Column, String, Text, UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Rol(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)

    usuarios = relationship("Usuario", back_populates="rol")
