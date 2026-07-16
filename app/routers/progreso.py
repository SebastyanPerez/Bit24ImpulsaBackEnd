import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.core.dependencies import get_current_user, require_admin_or_responsable
from app.models.progreso import Progreso
from app.models.usuarios import Usuario
from app.models.roles import Rol
from app.models.rutas import Ruta
from app.models.tareas import Tarea
from app.schemas.progreso import ProgresoOut, ProgresoUpdate

router = APIRouter(prefix="/progreso", tags=["progreso"])

@router.get("/me", response_model=List[ProgresoOut])
def get_progreso_me(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Retrieve details of tasks progress for the currently authenticated user."""
    return (
        db.query(Progreso)
        .options(joinedload(Progreso.tarea))
        .filter(Progreso.usuario_id == current_user.id)
        .all()
    )

@router.put("/{tarea_id}", response_model=ProgresoOut)
def update_progreso(
    tarea_id: uuid.UUID,
    progreso_in: ProgresoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Mark a task progress state as Pendiente, En Proceso, or Completado."""
    # Ensure task exists and is active
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id, Tarea.estado == True).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o inactiva"
        )

    # Search for an existing progress record
    db_progreso = (
        db.query(Progreso)
        .options(joinedload(Progreso.tarea))
        .filter(
            Progreso.usuario_id == current_user.id,
            Progreso.tarea_id == tarea_id
        )
        .first()
    )

    old_estado = db_progreso.estado if db_progreso else None
    new_estado = progreso_in.estado

    if not db_progreso:
        db_progreso = Progreso(
            usuario_id=current_user.id,
            tarea_id=tarea_id,
            estado=new_estado
        )
        if new_estado == "Completado":
            db_progreso.fecha_completado = datetime.utcnow()
        db.add(db_progreso)
    else:
        db_progreso.estado = new_estado
        if new_estado == "Completado" and old_estado != "Completado":
            db_progreso.fecha_completado = datetime.utcnow()
        elif new_estado != "Completado":
            db_progreso.fecha_completado = None

    db.commit()
    db.refresh(db_progreso)

    # Log activity when task is marked as Completado
    if new_estado == "Completado" and old_estado != "Completado":
        from app.core.actividad_service import registrar_actividad
        registrar_actividad(
            db,
            current_user.id,
            "Progreso",
            f"Completó la tarea '{tarea.titulo}'",
            referencia_id=tarea_id
        )

    return db_progreso

@router.get("/resumen")
def get_progreso_resumen(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin_or_responsable)
):
    """Aggregates progress completion stats by user role to feed the dashboard."""
    roles = db.query(Rol).all()
    resumen = []

    for rol in roles:
        # Get active users having this role ID
        usuarios_rol = db.query(Usuario).filter(Usuario.rol_id == rol.id, Usuario.estado == True).all()
        cant_usuarios = len(usuarios_rol)

        # Get active tasks in routes assigned to this role ID
        tareas_rol = db.query(Tarea).join(Ruta).filter(Ruta.rol_id == rol.id, Tarea.estado == True).all()
        cant_tareas = len(tareas_rol)

        if cant_usuarios == 0 or cant_tareas == 0:
            porcentaje = 0
            cant_completadas = 0
        else:
            user_ids = [u.id for u in usuarios_rol]
            tarea_ids = [t.id for t in tareas_rol]
            cant_completadas = (
                db.query(Progreso)
                .filter(
                    Progreso.usuario_id.in_(user_ids),
                    Progreso.tarea_id.in_(tarea_ids),
                    Progreso.estado == "Completado"
                )
                .count()
            )
            total_esperado = cant_usuarios * cant_tareas
            porcentaje = round((cant_completadas / total_esperado) * 100)

        resumen.append({
            "rol_id": str(rol.id),
            "rol_nombre": rol.nombre,
            "usuarios_activos": cant_usuarios,
            "tareas_activas": cant_tareas,
            "tareas_completadas": cant_completadas,
            "porcentaje_adopcion": porcentaje
        })

    return resumen
