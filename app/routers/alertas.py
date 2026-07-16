import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.core.dependencies import get_current_user, require_admin_or_responsable
from app.models.alertas import Alerta
from app.models.usuarios import Usuario
from app.schemas.alertas import AlertaOut, AlertaCreate

router = APIRouter(prefix="/alertas", tags=["alertas"])

@router.get("/me", response_model=List[AlertaOut])
def get_alertas_me(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retrieve alerts sent to the currently authenticated user, ordered by fecha_envio descending."""
    return (
        db.query(Alerta)
        .options(joinedload(Alerta.usuario))
        .filter(Alerta.usuario_id == current_user.id)
        .order_by(Alerta.fecha_envio.desc())
        .all()
    )

@router.put("/{id}/leer", response_model=AlertaOut)
def leer_alerta(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Mark the authenticated user's own alert as 'Leída'."""
    alerta = (
        db.query(Alerta)
        .options(joinedload(Alerta.usuario))
        .filter(Alerta.id == id, Alerta.usuario_id == current_user.id)
        .first()
    )
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    alerta.estado = "Leída"
    db.commit()
    db.refresh(alerta)
    return alerta

@router.post("", response_model=AlertaOut, status_code=status.HTTP_201_CREATED)
def create_alerta(
    alerta_in: AlertaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin_or_responsable)
):
    """Create a manual alert for a specific user (Admin or Responsable Interno only)."""
    target = db.query(Usuario).filter(Usuario.id == alerta_in.usuario_id).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario destino no existe"
        )

    db_alerta = Alerta(
        usuario_id=alerta_in.usuario_id,
        titulo=alerta_in.titulo,
        mensaje=alerta_in.mensaje,
        tipo=alerta_in.tipo,
        canal=alerta_in.canal,
        estado="Pendiente",
        accion_recomendada=alerta_in.accion_recomendada,
        fecha_envio=datetime.utcnow()
    )
    db.add(db_alerta)
    db.commit()
    db.refresh(db_alerta)

    from app.core.actividad_service import registrar_actividad
    registrar_actividad(
        db,
        current_user.id,
        "Alertas",
        f"Creó la alerta '{db_alerta.titulo}'",
        referencia_id=db_alerta.id
    )
    
    return (
        db.query(Alerta)
        .options(joinedload(Alerta.usuario))
        .filter(Alerta.id == db_alerta.id)
        .first()
    )

@router.get("", response_model=List[AlertaOut])
def get_all_alertas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin_or_responsable)
):
    """Retrieve all alerts for all users (Admin or Responsable Interno only)."""
    return (
        db.query(Alerta)
        .options(joinedload(Alerta.usuario))
        .order_by(Alerta.fecha_envio.desc())
        .all()
    )

@router.put("/{id}/atender", response_model=AlertaOut)
def atender_alerta(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin_or_responsable)
):
    """Mark an alert as 'Atendida' and set fecha_atendida to now (Admin or Responsable Interno only)."""
    alerta = (
        db.query(Alerta)
        .options(joinedload(Alerta.usuario))
        .filter(Alerta.id == id)
        .first()
    )
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    alerta.estado = "Atendida"
    alerta.fecha_atendida = datetime.utcnow()
    db.commit()
    db.refresh(alerta)
    return alerta
