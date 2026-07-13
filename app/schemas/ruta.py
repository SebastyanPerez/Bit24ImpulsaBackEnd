import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

class RutaBase(BaseModel):
    rol_id: uuid.UUID
    nombre: str
    descripcion: Optional[str] = None

class RutaCreate(RutaBase):
    pass

class RutaUpdate(BaseModel):
    rol_id: Optional[uuid.UUID] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[bool] = None

class RutaOut(RutaBase):
    id: uuid.UUID
    estado: bool

    model_config = ConfigDict(from_attributes=True)
