import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict

class UsuarioSimpleOut(BaseModel):
    nombre: str
    correo: str

    model_config = ConfigDict(from_attributes=True)

class AlertaOut(BaseModel):
    id: uuid.UUID
    usuario_id: uuid.UUID
    titulo: str
    mensaje: str
    tipo: Optional[str] = None
    canal: str
    estado: str
    accion_recomendada: Optional[str] = None
    fecha_envio: datetime
    fecha_atendida: Optional[datetime] = None
    usuario: UsuarioSimpleOut

    model_config = ConfigDict(from_attributes=True)

class AlertaCreate(BaseModel):
    usuario_id: uuid.UUID
    titulo: str
    mensaje: str
    tipo: Optional[str] = None
    canal: Literal["WhatsApp", "Email", "Sistema"]
    accion_recomendada: Optional[str] = None

class AlertaUpdateEstado(BaseModel):
    estado: Literal["Pendiente", "Leída", "Atendida"]
