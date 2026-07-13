import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

class TareaBase(BaseModel):
    ruta_id: uuid.UUID
    titulo: str
    descripcion: Optional[str] = None
    orden: int = 1

class TareaCreate(TareaBase):
    pass

class TareaUpdate(BaseModel):
    ruta_id: Optional[uuid.UUID] = None
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    orden: Optional[int] = None
    estado: Optional[bool] = None

class TareaOut(TareaBase):
    id: uuid.UUID
    estado: bool

    model_config = ConfigDict(from_attributes=True)
