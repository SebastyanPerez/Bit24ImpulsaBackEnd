from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.core.dependencies import require_admin_or_responsable
from app.models.actividad import Actividad
from app.models.usuarios import Usuario
from app.schemas.actividad import ActividadOut

router = APIRouter(prefix="/actividad", tags=["actividad"])

@router.get("/reciente", response_model=List[ActividadOut])
def get_actividad_reciente(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin_or_responsable)
):
    """
    Retrieve the last 30 activities recorded in the system.
    Only accessible by Admin or Responsable Interno.
    """
    return (
        db.query(Actividad)
        .options(joinedload(Actividad.usuario))
        .order_by(Actividad.created_at.desc())
        .limit(30)
        .all()
    )
