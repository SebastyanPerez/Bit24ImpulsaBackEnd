import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.core.dependencies import get_current_user, require_admin_or_responsable
from app.models.soporte import Soporte
from app.models.categorias_soporte import CategoriaSoporte
from app.models.usuarios import Usuario
from app.schemas.soporte import (
    CategoriaSoporteOut,
    SoporteOut,
    SoporteCreate,
    SoporteAsignar,
    SoporteUpdateEstado
)

router = APIRouter(prefix="", tags=["soporte"])

@router.get("/categorias-soporte", response_model=List[CategoriaSoporteOut], dependencies=[Depends(get_current_user)])
def get_categorias_soporte(db: Session = Depends(get_db)):
    """List all soporte categories (Public for authenticated users)."""
    return db.query(CategoriaSoporte).all()

@router.post("/soporte", response_model=SoporteOut, status_code=status.HTTP_201_CREATED)
def create_soporte(
    soporte_in: SoporteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a new support ticket."""
    # Check if category exists
    category = db.query(CategoriaSoporte).filter(CategoriaSoporte.id == soporte_in.categoria_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La categoría especificada no existe"
        )
    
    db_soporte = Soporte(
        id=uuid.uuid4(),
        usuario_id=current_user.id,
        categoria_id=soporte_in.categoria_id,
        titulo=soporte_in.titulo,
        descripcion=soporte_in.descripcion,
        estado="Abierto"
    )
    db.add(db_soporte)
    db.commit()
    
    from app.core.actividad_service import registrar_actividad
    registrar_actividad(
        db,
        current_user.id,
        "Soporte",
        f"Creó el ticket '{db_soporte.titulo}'",
        referencia_id=db_soporte.id
    )
    
    # Reload with relationships
    return (
        db.query(Soporte)
        .options(
            joinedload(Soporte.usuario),
            joinedload(Soporte.categoria),
            joinedload(Soporte.responsable)
        )
        .filter(Soporte.id == db_soporte.id)
        .first()
    )

@router.get("/soporte/me", response_model=List[SoporteOut])
def get_soporte_me(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """List support tickets registered by the current user."""
    return (
        db.query(Soporte)
        .options(
            joinedload(Soporte.usuario),
            joinedload(Soporte.categoria),
            joinedload(Soporte.responsable)
        )
        .filter(Soporte.usuario_id == current_user.id)
        .all()
    )

@router.get("/soporte", response_model=List[SoporteOut])
def get_all_soportes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin_or_responsable)
):
    """List all support tickets (Admin or Responsable Interno only)."""
    return (
        db.query(Soporte)
        .options(
            joinedload(Soporte.usuario),
            joinedload(Soporte.categoria),
            joinedload(Soporte.responsable)
        )
        .all()
    )

@router.put("/soporte/{id}/asignar", response_model=SoporteOut)
def asignar_soporte(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin_or_responsable)
):
    """Assign the authenticated user as the responsible user to a ticket and set its state to 'En Proceso'."""
    ticket = db.query(Soporte).filter(Soporte.id == id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket de soporte no encontrado"
        )
        
    ticket.responsable_id = current_user.id
    ticket.estado = "En Proceso"
    db.commit()
    db.refresh(ticket)
    
    # Reload relationships to ensure serialization works correctly
    return (
        db.query(Soporte)
        .options(
            joinedload(Soporte.usuario),
            joinedload(Soporte.categoria),
            joinedload(Soporte.responsable)
        )
        .filter(Soporte.id == id)
        .first()
    )

@router.put("/soporte/{id}/estado", response_model=SoporteOut)
def update_soporte_estado(
    id: uuid.UUID,
    soporte_in: SoporteUpdateEstado,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin_or_responsable)
):
    """Update the status of a support ticket."""
    ticket = db.query(Soporte).filter(Soporte.id == id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket de soporte no encontrado"
        )
        
    ticket.estado = soporte_in.estado
    db.commit()
    db.refresh(ticket)
    
    from app.core.actividad_service import registrar_actividad
    registrar_actividad(
        db,
        current_user.id,
        "Soporte",
        f"Respondió/cerró el ticket '{ticket.titulo}'",
        referencia_id=ticket.id
    )
    
    return (
        db.query(Soporte)
        .options(
            joinedload(Soporte.usuario),
            joinedload(Soporte.categoria),
            joinedload(Soporte.responsable)
        )
        .filter(Soporte.id == id)
        .first()
    )
