import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

class RolOut(BaseModel):
    id: uuid.UUID
    nombre: str
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UsuarioOut(BaseModel):
    id: uuid.UUID
    nombre: str
    apellido: str
    correo: str
    rol_id: Optional[uuid.UUID] = None
    rol: Optional[RolOut] = None

    model_config = ConfigDict(from_attributes=True)

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
    password: Optional[str] = None
    rol_id: Optional[uuid.UUID] = None

