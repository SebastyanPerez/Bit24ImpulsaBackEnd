import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.rutas import Ruta
from app.models.tareas import Tarea
from app.models.guias import Guia
from app.schemas.tarea import TareaCreate, TareaUpdate, TareaOut
from app.schemas.guia import GuiaOut

router = APIRouter(prefix="/tareas", tags=["tareas"])

@router.get("", response_model=List[TareaOut], dependencies=[Depends(get_current_user)])
def list_tareas(db: Session = Depends(get_db)):
    """List all active tasks in the system."""
    return db.query(Tarea).filter(Tarea.estado == True).all()

@router.get("/{id}", response_model=TareaOut, dependencies=[Depends(get_current_user)])
def get_tarea(id: uuid.UUID, db: Session = Depends(get_db)):
    """Get details of a specific active task."""
    tarea = db.query(Tarea).filter(Tarea.id == id, Tarea.estado == True).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    return tarea

@router.get("/{tarea_id}/guias", response_model=List[GuiaOut], dependencies=[Depends(get_current_user)])
def list_guias_por_tarea(tarea_id: uuid.UUID, db: Session = Depends(get_db)):
    """List all active guides for a specific active task."""
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id, Tarea.estado == True).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o inactiva"
        )
    return db.query(Guia).filter(Guia.tarea_id == tarea_id, Guia.estado == True).all()

@router.post("", response_model=TareaOut, status_code=status.HTTP_201_CREATED)
def create_tarea(tarea_in: TareaCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Create a new task (Admin only)."""
    ruta = db.query(Ruta).filter(Ruta.id == tarea_in.ruta_id, Ruta.estado == True).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La ruta especificada no existe o está inactiva"
        )
    
    db_tarea = Tarea(
        ruta_id=tarea_in.ruta_id,
        titulo=tarea_in.titulo,
        descripcion=tarea_in.descripcion,
        orden=tarea_in.orden,
        estado=True
    )
    db.add(db_tarea)
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

@router.put("/{id}", response_model=TareaOut)
def update_tarea(id: uuid.UUID, tarea_in: TareaUpdate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Update a task (Admin only)."""
    tarea = db.query(Tarea).filter(Tarea.id == id, Tarea.estado == True).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    if tarea_in.ruta_id is not None:
        ruta = db.query(Ruta).filter(Ruta.id == tarea_in.ruta_id, Ruta.estado == True).first()
        if not ruta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La ruta especificada no existe o está inactiva"
            )
        tarea.ruta_id = tarea_in.ruta_id
        
    if tarea_in.titulo is not None:
        tarea.titulo = tarea_in.titulo
    if tarea_in.descripcion is not None:
        tarea.descripcion = tarea_in.descripcion
    if tarea_in.orden is not None:
        tarea.orden = tarea_in.orden
    if tarea_in.estado is not None:
        tarea.estado = tarea_in.estado
        
    db.commit()
    db.refresh(tarea)
    return tarea

@router.delete("/{id}", response_model=TareaOut)
def delete_tarea(id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Soft delete a task by setting estado=False (Admin only)."""
    tarea = db.query(Tarea).filter(Tarea.id == id, Tarea.estado == True).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o ya eliminada"
        )
    
    tarea.estado = False
    db.commit()
    db.refresh(tarea)
    return tarea
