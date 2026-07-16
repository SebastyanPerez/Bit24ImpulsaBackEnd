import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UsuarioSimpleOut(BaseModel):
    nombre: str
    apellido: str

    model_config = ConfigDict(from_attributes=True)

class ActividadOut(BaseModel):
    id: uuid.UUID
    usuario: UsuarioSimpleOut
    modulo: str
    accion: str
    referencia_id: Optional[uuid.UUID] = None
    detalle: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
