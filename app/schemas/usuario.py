import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

class UsuarioOut(BaseModel):
    id: uuid.UUID
    nombre: str
    apellido: str
    correo: str
    rol_id: Optional[uuid.UUID] = None

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

