import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

class GuiaBase(BaseModel):
    tarea_id: uuid.UUID
    titulo: str
    contenido: Optional[str] = None
    video_url: Optional[str] = None
    duracion: Optional[int] = None

class GuiaCreate(GuiaBase):
    pass

class GuiaUpdate(BaseModel):
    tarea_id: Optional[uuid.UUID] = None
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    video_url: Optional[str] = None
    duracion: Optional[int] = None
    estado: Optional[bool] = None

class GuiaOut(GuiaBase):
    id: uuid.UUID
    estado: bool

    model_config = ConfigDict(from_attributes=True)
