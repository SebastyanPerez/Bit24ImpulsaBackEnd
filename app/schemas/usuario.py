import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.rol import RolOut


class UsuarioOut(BaseModel):
    id: uuid.UUID
    nombre: str
    apellido: str
    correo: str
    rol_id: Optional[uuid.UUID] = None
    rol: Optional[RolOut] = None
    estado: bool
    fecha_creacion: datetime = Field(validation_alias="created_at")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    password: str
    rol_id: Optional[uuid.UUID] = None


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[EmailStr] = None
    rol_id: Optional[uuid.UUID] = None
    estado: Optional[bool] = None
