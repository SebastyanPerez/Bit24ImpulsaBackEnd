from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.core.dependencies import get_current_user, require_admin_or_responsable
from app.models.usuarios import Usuario
from app.models.roles import Rol
from app.models.progreso import Progreso
from app.models.alertas import Alerta
from app.models.soporte import Soporte
from app.models.actividad import Actividad
from app.models.rutas import Ruta
from app.models.tareas import Tarea

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Protected dashboard endpoint returning real database metrics."""
    # 1. Alertas activas: COUNT of alerts state != 'Atendida'
    alertas_activas = db.query(Alerta).filter(Alerta.estado != "Atendida").count()

    # 2. Casos de soporte: grouped by ticket state
    pendiente = db.query(Soporte).filter(Soporte.estado == "Abierto").count()
    en_proceso = db.query(Soporte).filter(Soporte.estado == "En Proceso").count()
    resuelto = db.query(Soporte).filter(Soporte.estado == "Resuelto").count()
    cerrado = db.query(Soporte).filter(Soporte.estado == "Cerrado").count()
    total = db.query(Soporte).count()

    # 3. Tasks for the authenticated user based on role
    mis_tareas_recientes = []
    user_tasks = []
    if current_user.rol_id:
        ruta = db.query(Ruta).filter(Ruta.rol_id == current_user.rol_id, Ruta.estado == True).first()
        if ruta:
            user_tasks = db.query(Tarea).filter(Tarea.ruta_id == ruta.id, Tarea.estado == True).order_by(Tarea.orden).all()
            for t in user_tasks:
                prog = db.query(Progreso).filter(
                    Progreso.usuario_id == current_user.id,
                    Progreso.tarea_id == t.id
                ).first()
                status_val = "pendiente"
                if prog:
                    if prog.estado == "Completado":
                        status_val = "completado"
                    elif prog.estado == "En Proceso":
                        status_val = "en_proceso"
                mis_tareas_recientes.append({
                    "id": str(t.id),
                    "title": t.titulo,
                    "status": status_val
                })

    # 4. Avance por área calculation
    collaborator_roles = ["Ventas", "Caja", "Almacén", "Compras", "Administración"]
    roles_in_db = db.query(Rol).filter(Rol.nombre.in_(collaborator_roles)).all()
    avance_por_area = []
    
    for r in roles_in_db:
        usuarios_rol = db.query(Usuario).filter(Usuario.rol_id == r.id, Usuario.estado == True).all()
        cant_usuarios = len(usuarios_rol)
        tareas_rol = db.query(Tarea).join(Ruta).filter(Ruta.rol_id == r.id, Tarea.estado == True).all()
        cant_tareas = len(tareas_rol)
        if cant_usuarios == 0 or cant_tareas == 0:
            porcentaje = 0
        else:
            u_ids = [u.id for u in usuarios_rol]
            t_ids = [t.id for t in tareas_rol]
            completed = db.query(Progreso).filter(
                Progreso.usuario_id.in_(u_ids),
                Progreso.tarea_id.in_(t_ids),
                Progreso.estado == "Completado"
            ).count()
            porcentaje = round((completed / (cant_usuarios * cant_tareas)) * 100)
        avance_por_area.append({
            "area": r.nombre,
            "progress": porcentaje
        })

    # 5. Recommendation message
    pending_rec = next((x for x in mis_tareas_recientes if x["status"] != "completado"), None)
    rol_name = current_user.rol.nombre if current_user.rol else "tu área"
    if pending_rec:
        recomendacion = f"Hola {current_user.nombre}. Según tu avance en {rol_name}, te recomendamos completar \"{pending_rec['title']}\" hoy. Esto subirá tu adopción del área al menos 8 puntos."
    else:
        recomendacion = f"¡Excelente trabajo, {current_user.nombre}! Has completado todas las tareas de la ruta de {rol_name}."

    # 6. User metrics calculation
    completed_user = db.query(Progreso).filter(
        Progreso.usuario_id == current_user.id,
        Progreso.tarea_id.in_([t.id for t in user_tasks]) if user_tasks else Progreso.tarea_id.in_([]),
        Progreso.estado == "Completado"
    ).count() if user_tasks else 0

    role_name = current_user.rol.nombre if current_user.rol else ""
    is_admin_or_resp = role_name in ["Administrador", "Responsable Interno"]
    
    if is_admin_or_resp:
        adopcion_avg = round(sum(a["progress"] for a in avance_por_area) / len(avance_por_area)) if avance_por_area else 0
        progreso_pct = adopcion_avg
    else:
        progreso_pct = round((completed_user / len(user_tasks)) * 100) if user_tasks else 0

    return {
        "alertas_activas": alertas_activas,
        "casos_soporte": {
            "total": total,
            "pendiente": pendiente,
            "en_proceso": en_proceso,
            "resuelto": resuelto,
            "cerrado": cerrado
        },
        "mis_tareas_recientes": mis_tareas_recientes,
        "avance_por_area": avance_por_area,
        "recomendacion": recomendacion,
        "metrics": {
            "progreso_general_porcentaje": progreso_pct,
            "tareas_completadas": completed_user,
            "tareas_pendientes": len(user_tasks) - completed_user
        }
    }

def normalize_area_name(name: str) -> str:
    n = name.lower().strip()
    if "venta" in n: return "Ventas"
    if "caja" in n: return "Caja"
    if "almac" in n: return "Almacén"
    if "compra" in n: return "Compras"
    if "administra" in n: return "Administración"
    return name

@router.get("/responsable")
def get_dashboard_responsable(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin_or_responsable)
):
    """
    Retrieve real statistics for the internal responsible dashboard page.
    Only accessible by Admin or Responsable Interno.
    """
    collaborator_roles = ["Ventas", "Caja", "Almacén", "Compras", "Administración"]
    roles_in_db = db.query(Rol).filter(Rol.nombre.in_(collaborator_roles)).all()

    res_details = []
    percentages = []

    # Area color tokens
    colors = {
        "Ventas": "#5D1451",
        "Caja": "#3DB1AA",
        "Almacén": "#ffd37f",
        "Compras": "#8a2b7a",
        "Administración": "#3DB1AA"
    }

    def get_recommendation(area: str, progress: int) -> str:
        if progress < 50:
            return "Retomar inmediatamente — sin actividad"
        if area == "Ventas":
            return "Completar módulo de comprobantes" if progress < 70 else "Continuar con módulo de comprobantes"
        elif area == "Caja":
            return "Completar módulo de cierre de caja" if progress < 70 else "Avance óptimo — continuar con conciliaciones"
        elif area == "Almacén":
            return "Actualizar stock disponible" if progress < 70 else "Avance óptimo — continuar con el conteo"
        elif area == "Compras":
            return "Asignar responsable y completar aprobaciones" if progress < 70 else "Continuar con órdenes de compra"
        elif area == "Administración":
            return "Revisar configuraciones de permisos" if progress < 70 else "Avance óptimo — continuar con reportes"
        return "Continuar con las tareas de adopción"

    for area_name in collaborator_roles:
        rol = next((r for r in roles_in_db if r.nombre == area_name), None)
        if not rol:
            res_details.append({
                "area": area_name,
                "user": "Sin asignar",
                "progress": 0,
                "lastActivity": "Sin actividad",
                "risk": "alto",
                "action": get_recommendation(area_name, 0),
                "color": colors.get(area_name, "#666666")
            })
            percentages.append(0)
            continue

        # Get active users
        users = db.query(Usuario).filter(Usuario.rol_id == rol.id, Usuario.estado == True).all()
        user_name = f"{users[0].nombre} {users[0].apellido}" if users else "Sin asignar"

        # Tasks
        tasks = db.query(Tarea).join(Ruta).filter(Ruta.rol_id == rol.id, Tarea.estado == True).all()
        
        progress_val = 0
        if users and tasks:
            user_ids = [u.id for u in users]
            task_ids = [t.id for t in tasks]
            completed = db.query(Progreso).filter(
                Progreso.usuario_id.in_(user_ids),
                Progreso.tarea_id.in_(task_ids),
                Progreso.estado == "Completado"
            ).count()
            progress_val = round((completed / (len(users) * len(tasks))) * 100)
        
        percentages.append(progress_val)

        # Risk
        risk = "bajo"
        if progress_val < 50:
            risk = "alto"
        elif progress_val < 70:
            risk = "medio"

        # Last activity
        last_act_str = "Sin actividad"
        if users:
            user_ids = [u.id for u in users]
            latest_act = db.query(Actividad).filter(Actividad.usuario_id.in_(user_ids)).order_by(Actividad.created_at.desc()).first()
            if latest_act:
                diff = datetime.utcnow() - latest_act.created_at
                if diff.days > 0:
                    last_act_str = f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
                elif diff.seconds >= 3600:
                    hours = diff.seconds // 3600
                    last_act_str = f"hace {hours} hora{'s' if hours > 1 else ''}"
                else:
                    mins = max(1, diff.seconds // 60)
                    last_act_str = f"hace {mins} min"
            else:
                # Fallback to progreso created_at
                latest_prog = db.query(Progreso).filter(
                    Progreso.usuario_id.in_(user_ids),
                    Progreso.estado == "Completado"
                ).order_by(Progreso.fecha_completado.desc()).first()
                if latest_prog and latest_prog.fecha_completado:
                    diff = datetime.utcnow() - latest_prog.fecha_completado
                    if diff.days > 0:
                        last_act_str = f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
                    elif diff.seconds >= 3600:
                        hours = db.query(Actividad).count() # dummy
                        hours = diff.seconds // 3600
                        last_act_str = f"hace {hours} hora{'s' if hours > 1 else ''}"
                    else:
                        mins = max(1, diff.seconds // 60)
                        last_act_str = f"hace {mins} min"

        res_details.append({
            "area": area_name,
            "user": user_name,
            "progress": progress_val,
            "lastActivity": last_act_str,
            "risk": risk,
            "action": get_recommendation(area_name, progress_val),
            "color": colors.get(area_name, "#666666")
        })

    # Compute global KPIs
    adopcion_global = round(sum(percentages) / len(percentages)) if percentages else 0

    # Areas en riesgo alto: progress < 50 OR has pending alerts
    areas_riesgo_count = 0
    for idx, area_name in enumerate(collaborator_roles):
        p = percentages[idx]
        if p < 50:
            areas_riesgo_count += 1
            continue
        rol = next((r for r in roles_in_db if r.nombre == area_name), None)
        if rol:
            users = db.query(Usuario).filter(Usuario.rol_id == rol.id, Usuario.estado == True).all()
            if users:
                u_ids = [u.id for u in users]
                pending_alerts = db.query(Alerta).filter(Alerta.usuario_id.in_(u_ids), Alerta.estado != "Atendida").count()
                if pending_alerts > 0:
                    areas_riesgo_count += 1

    # Active users
    time_24h = datetime.utcnow() - timedelta(hours=24)
    activos_ids = db.query(Actividad.usuario_id).filter(Actividad.created_at >= time_24h).distinct().all()
    activos_count = len(activos_ids)
    total_users = db.query(Usuario).filter(Usuario.estado == True).count()

    active_user_models = db.query(Usuario).filter(Usuario.id.in_([uid[0] for uid in activos_ids])).all()
    active_areas = set()
    for au in active_user_models:
        if au.rol:
            active_areas.add(normalize_area_name(au.rol.nombre))
    active_areas_str = ", ".join(sorted(list(active_areas))) if active_areas else "Ninguna"

    tickets_abiertos = db.query(Soporte).filter(Soporte.estado.notin_(["Resuelto", "Cerrado"])).count()

    return {
        "adopcion_global": adopcion_global,
        "areas_riesgo_alto": areas_riesgo_count,
        "usuarios_activos": f"{activos_count}/{total_users}",
        "usuarios_activos_sub": active_areas_str,
        "tickets_abiertos": tickets_abiertos,
        "avance_areas_detalle": res_details
    }
