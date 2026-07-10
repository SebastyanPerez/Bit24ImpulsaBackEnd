import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RolOut(BaseModel):
    id: uuid.UUID
    nombre: str
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
