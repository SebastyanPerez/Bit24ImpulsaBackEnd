import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PreguntaCreate(BaseModel):
    pregunta: str
    tarea_id: Optional[uuid.UUID] = None
    guia_id: Optional[uuid.UUID] = None

class PreguntaOut(BaseModel):
    id: uuid.UUID
    pregunta: str
    respuesta: Optional[str] = None
    categoria: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
