import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict
from app.schemas.usuario import UsuarioOut

class CategoriaSoporteOut(BaseModel):
    id: uuid.UUID
    nombre: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SoporteOut(BaseModel):
    id: uuid.UUID
    usuario_id: uuid.UUID
    categoria_id: uuid.UUID
    responsable_id: Optional[uuid.UUID] = None
    titulo: str
    descripcion: Optional[str] = None
    estado: str
    created_at: datetime
    
    usuario: UsuarioOut
    categoria: CategoriaSoporteOut
    responsable: Optional[UsuarioOut] = None

    model_config = ConfigDict(from_attributes=True)

class SoporteCreate(BaseModel):
    categoria_id: uuid.UUID
    titulo: str
    descripcion: Optional[str] = None

class SoporteAsignar(BaseModel):
    responsable_id: uuid.UUID

class SoporteUpdateEstado(BaseModel):
    estado: Literal["Abierto", "En Proceso", "Resuelto", "Cerrado"]
