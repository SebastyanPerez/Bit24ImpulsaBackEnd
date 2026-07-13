import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.rutas import Ruta
from app.models.roles import Rol
from app.models.tareas import Tarea
from app.schemas.ruta import RutaCreate, RutaUpdate, RutaOut
from app.schemas.tarea import TareaOut

router = APIRouter(prefix="/rutas", tags=["rutas"])

@router.get("", response_model=List[RutaOut], dependencies=[Depends(get_current_user)])
def list_rutas(db: Session = Depends(get_db)):
    """List all active routes in the system."""
    return db.query(Ruta).filter(Ruta.estado == True).all()

@router.get("/{id}", response_model=RutaOut, dependencies=[Depends(get_current_user)])
def get_ruta(id: uuid.UUID, db: Session = Depends(get_db)):
    """Get details of a specific active route."""
    ruta = db.query(Ruta).filter(Ruta.id == id, Ruta.estado == True).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )
    return ruta

@router.get("/{ruta_id}/tareas", response_model=List[TareaOut], dependencies=[Depends(get_current_user)])
def list_tareas_por_ruta(ruta_id: uuid.UUID, db: Session = Depends(get_db)):
    """List all active tasks for a specific active route."""
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id, Ruta.estado == True).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada o inactiva"
        )
    return db.query(Tarea).filter(Tarea.ruta_id == ruta_id, Tarea.estado == True).order_by(Tarea.orden.asc()).all()

@router.post("", response_model=RutaOut, status_code=status.HTTP_201_CREATED)
def create_ruta(ruta_in: RutaCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Create a new route (Admin only)."""
    rol = db.query(Rol).filter(Rol.id == ruta_in.rol_id).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El rol especificado no existe"
        )
    
    db_ruta = Ruta(
        rol_id=ruta_in.rol_id,
        nombre=ruta_in.nombre,
        descripcion=ruta_in.descripcion,
        estado=True
    )
    db.add(db_ruta)
    db.commit()
    db.refresh(db_ruta)
    return db_ruta

@router.put("/{id}", response_model=RutaOut)
def update_ruta(id: uuid.UUID, ruta_in: RutaUpdate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Update a route (Admin only)."""
    ruta = db.query(Ruta).filter(Ruta.id == id, Ruta.estado == True).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada"
        )
    
    if ruta_in.rol_id is not None:
        rol = db.query(Rol).filter(Rol.id == ruta_in.rol_id).first()
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El rol especificado no existe"
            )
        ruta.rol_id = ruta_in.rol_id
        
    if ruta_in.nombre is not None:
        ruta.nombre = ruta_in.nombre
    if ruta_in.descripcion is not None:
        ruta.descripcion = ruta_in.descripcion
    if ruta_in.estado is not None:
        ruta.estado = ruta_in.estado
        
    db.commit()
    db.refresh(ruta)
    return ruta

@router.delete("/{id}", response_model=RutaOut)
def delete_ruta(id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Soft delete a route by setting estado=False (Admin only)."""
    ruta = db.query(Ruta).filter(Ruta.id == id, Ruta.estado == True).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada o ya eliminada"
        )
    
    ruta.estado = False
    db.commit()
    db.refresh(ruta)
    return ruta
