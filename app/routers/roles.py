from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import require_admin
from app.models.roles import Rol
from app.schemas.usuario import RolOut

router = APIRouter(prefix="/roles", tags=["roles"], dependencies=[Depends(require_admin)])

@router.get("", response_model=List[RolOut])
def list_roles(db: Session = Depends(get_db)):
    """List all roles in the system."""
    return db.query(Rol).all()
