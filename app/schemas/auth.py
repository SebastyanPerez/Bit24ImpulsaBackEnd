from pydantic import BaseModel, EmailStr
from app.schemas.usuario import UsuarioOut

class UsuarioLogin(BaseModel):
    correo: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioOut
