from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import require_admin
from app.models.roles import Rol
from app.schemas.rol import RolOut

router = APIRouter(prefix="/roles", tags=["roles"], dependencies=[Depends(require_admin)])


@router.get("", response_model=List[RolOut])
def list_roles(db: Session = Depends(get_db)):
    """List all roles in the system ordered alphabetically by name."""
    return db.query(Rol).order_by(Rol.nombre.asc()).all()
