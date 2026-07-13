import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.tareas import Tarea
from app.models.guias import Guia
from app.schemas.guia import GuiaCreate, GuiaUpdate, GuiaOut

router = APIRouter(prefix="/guias", tags=["guias"])

@router.get("", response_model=List[GuiaOut], dependencies=[Depends(get_current_user)])
def list_guias(db: Session = Depends(get_db)):
    """List all active guides in the system."""
    return db.query(Guia).filter(Guia.estado == True).all()

@router.get("/{id}", response_model=GuiaOut, dependencies=[Depends(get_current_user)])
def get_guia(id: uuid.UUID, db: Session = Depends(get_db)):
    """Get details of a specific active guide."""
    guia = db.query(Guia).filter(Guia.id == id, Guia.estado == True).first()
    if not guia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guía no encontrada"
        )
    return guia

@router.post("", response_model=GuiaOut, status_code=status.HTTP_201_CREATED)
def create_guia(guia_in: GuiaCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Create a new guide (Admin only)."""
    tarea = db.query(Tarea).filter(Tarea.id == guia_in.tarea_id, Tarea.estado == True).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La tarea especificada no existe o está inactiva"
        )
    
    db_guia = Guia(
        tarea_id=guia_in.tarea_id,
        titulo=guia_in.titulo,
        contenido=guia_in.contenido,
        video_url=guia_in.video_url,
        duracion=guia_in.duracion,
        estado=True
    )
    db.add(db_guia)
    db.commit()
    db.refresh(db_guia)
    return db_guia

@router.put("/{id}", response_model=GuiaOut)
def update_guia(id: uuid.UUID, guia_in: GuiaUpdate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Update a guide (Admin only)."""
    guia = db.query(Guia).filter(Guia.id == id, Guia.estado == True).first()
    if not guia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guía no encontrada"
        )
    
    if guia_in.tarea_id is not None:
        tarea = db.query(Tarea).filter(Tarea.id == guia_in.tarea_id, Tarea.estado == True).first()
        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La tarea especificada no existe o está inactiva"
            )
        guia.tarea_id = guia_in.tarea_id
        
    if guia_in.titulo is not None:
        guia.titulo = guia_in.titulo
    if guia_in.contenido is not None:
        guia.contenido = guia_in.contenido
    if guia_in.video_url is not None:
        guia.video_url = guia_in.video_url
    if guia_in.duracion is not None:
        guia.duracion = guia_in.duracion
    if guia_in.estado is not None:
        guia.estado = guia_in.estado
        
    db.commit()
    db.refresh(guia)
    return guia

@router.delete("/{id}", response_model=GuiaOut)
def delete_guia(id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Soft delete a guide by setting estado=False (Admin only)."""
    guia = db.query(Guia).filter(Guia.id == id, Guia.estado == True).first()
    if not guia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guía no encontrada o ya eliminada"
        )
    
    guia.estado = False
    db.commit()
    db.refresh(guia)
    return guia
