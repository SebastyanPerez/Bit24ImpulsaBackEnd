import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict

class TareaSimpleOut(BaseModel):
    id: uuid.UUID
    titulo: str
    
    model_config = ConfigDict(from_attributes=True)

class ProgresoOut(BaseModel):
    id: uuid.UUID
    usuario_id: uuid.UUID
    tarea_id: uuid.UUID
    estado: str
    fecha_completado: Optional[datetime] = None
    tarea: TareaSimpleOut

    model_config = ConfigDict(from_attributes=True)

class ProgresoUpdate(BaseModel):
    estado: Literal["Pendiente", "En Proceso", "Completado"]
