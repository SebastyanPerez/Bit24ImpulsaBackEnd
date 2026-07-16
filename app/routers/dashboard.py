from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from typing import List
import asyncio
from sqlalchemy import func

from app.database import get_db, SessionLocal
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

def format_time_diff(dt: datetime) -> str:
    if not dt:
        return "Sin actividad"
    diff = datetime.utcnow() - dt
    if diff.days > 0:
        return f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"hace {hours} hora{'s' if hours > 1 else ''}"
    else:
        mins = max(1, diff.seconds // 60)
        return f"hace {mins} min"

def fetch_alertas_activas() -> int:
    with SessionLocal() as db:
        return db.query(Alerta).filter(Alerta.estado != "Atendida").count()

def fetch_casos_soporte() -> dict:
    with SessionLocal() as db:
        soporte_stats = db.query(Soporte.estado, func.count(Soporte.id)).group_by(Soporte.estado).all()
        stats_dict = {estado: count for estado, count in soporte_stats}
        total = sum(stats_dict.values())
        return {
            "total": total,
            "pendiente": stats_dict.get("Abierto", 0),
            "en_proceso": stats_dict.get("En Proceso", 0),
            "resuelto": stats_dict.get("Resuelto", 0),
            "cerrado": stats_dict.get("Cerrado", 0)
        }

def fetch_user_tasks_and_progress(user_id, rol_id) -> tuple:
    with SessionLocal() as db:
        mis_tareas_recientes = []
        user_tasks = []
        if rol_id:
            ruta = db.query(Ruta).filter(Ruta.rol_id == rol_id, Ruta.estado == True).first()
            if ruta:
                user_tasks_models = db.query(Tarea).filter(Tarea.ruta_id == ruta.id, Tarea.estado == True).order_by(Tarea.orden).all()
                user_tasks = [{"id": str(t.id), "title": t.titulo} for t in user_tasks_models]
                if user_tasks:
                    t_ids = [t["id"] for t in user_tasks]
                    progresos = db.query(Progreso).filter(
                        Progreso.usuario_id == user_id,
                        Progreso.tarea_id.in_(t_ids)
                    ).all()
                    progreso_map = {str(p.tarea_id): p.estado for p in progresos}
                    for t in user_tasks:
                        status_val = "pendiente"
                        pe = progreso_map.get(t["id"])
                        if pe == "Completado":
                            status_val = "completado"
                        elif pe == "En Proceso":
                            status_val = "en_proceso"
                        mis_tareas_recientes.append({
                            "id": t["id"],
                            "title": t["title"],
                            "status": status_val
                        })
        return mis_tareas_recientes, user_tasks

def fetch_avance_por_area() -> list:
    with SessionLocal() as db:
        collaborator_roles = ["Ventas", "Caja", "Almacén", "Compras", "Administración"]
        roles_in_db = db.query(Rol).filter(Rol.nombre.in_(collaborator_roles)).all()
        rol_map = {r.nombre: r.id for r in roles_in_db}
        rol_ids = list(rol_map.values())
        
        # 1. Fetch active users by rol
        users = db.query(Usuario).filter(Usuario.rol_id.in_(rol_ids), Usuario.estado == True).all()
        users_by_rol = {}
        for u in users:
            users_by_rol.setdefault(u.rol_id, []).append(u.id)
            
        # 2. Fetch active tasks by rol (joined with Ruta)
        tasks = db.query(Tarea.id, Ruta.rol_id).join(Ruta).filter(Ruta.rol_id.in_(rol_ids), Tarea.estado == True).all()
        tasks_by_rol = {}
        for t_id, r_rol_id in tasks:
            tasks_by_rol.setdefault(r_rol_id, []).append(t_id)
            
        # 3. Fetch completed progresses for these users and tasks
        all_user_ids = [u.id for u in users]
        all_task_ids = [t_id for t_id, _ in tasks]
        completed_set = set()
        if all_user_ids and all_task_ids:
            completed_progs = db.query(Progreso.usuario_id, Progreso.tarea_id).filter(
                Progreso.usuario_id.in_(all_user_ids),
                Progreso.tarea_id.in_(all_task_ids),
                Progreso.estado == "Completado"
            ).all()
            completed_set = {(p_uid, p_tid) for p_uid, p_tid in completed_progs}
        
        # 4. Calculate progress per area
        avance_por_area = []
        for area_name in collaborator_roles:
            r_id = rol_map.get(area_name)
            if not r_id:
                avance_por_area.append({"area": area_name, "progress": 0})
                continue
            u_ids = users_by_rol.get(r_id, [])
            t_ids = tasks_by_rol.get(r_id, [])
            cant_usuarios = len(u_ids)
            cant_tareas = len(t_ids)
            if cant_usuarios == 0 or cant_tareas == 0:
                porcentaje = 0
            else:
                completed_count = sum(1 for uid in u_ids for tid in t_ids if (uid, tid) in completed_set)
                porcentaje = round((completed_count / (cant_usuarios * cant_tareas)) * 100)
            avance_por_area.append({
                "area": area_name,
                "progress": porcentaje
            })
        return avance_por_area

@router.get("")
async def get_dashboard_data(
    current_user: Usuario = Depends(get_current_user)
):
    """Protected dashboard endpoint returning real database metrics optimized and parallelized."""
    # Run operations concurrently
    alertas_task = asyncio.to_thread(fetch_alertas_activas)
    soporte_task = asyncio.to_thread(fetch_casos_soporte)
    user_tasks_task = asyncio.to_thread(fetch_user_tasks_and_progress, current_user.id, current_user.rol_id)
    avance_task = asyncio.to_thread(fetch_avance_por_area)

    alertas_activas, casos_soporte, (mis_tareas_recientes, user_tasks), avance_por_area = await asyncio.gather(
        alertas_task, soporte_task, user_tasks_task, avance_task
    )

    # recommendation message
    pending_rec = next((x for x in mis_tareas_recientes if x["status"] != "completado"), None)
    rol_name = current_user.rol.nombre if current_user.rol else "tu área"
    if pending_rec:
        recomendacion = f"Hola {current_user.nombre}. Según tu avance en {rol_name}, te recomendamos completar \"{pending_rec['title']}\" hoy. Esto subirá tu adopción del área al menos 8 puntos."
    else:
        recomendacion = f"¡Excelente trabajo, {current_user.nombre}! Has completado todas las tareas de la ruta de {rol_name}."

    # User metrics calculation
    completed_user = sum(1 for t in mis_tareas_recientes if t["status"] == "completado")

    role_name = current_user.rol.nombre if current_user.rol else ""
    is_admin_or_resp = role_name in ["Administrador", "Responsable Interno"]
    
    if is_admin_or_resp:
        adopcion_avg = round(sum(a["progress"] for a in avance_por_area) / len(avance_por_area)) if avance_por_area else 0
        progreso_pct = adopcion_avg
    else:
        progreso_pct = round((completed_user / len(user_tasks)) * 100) if user_tasks else 0

    return {
        "alertas_activas": alertas_activas,
        "casos_soporte": casos_soporte,
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

def fetch_dashboard_responsable_data() -> tuple:
    with SessionLocal() as db:
        collaborator_roles = ["Ventas", "Caja", "Almacén", "Compras", "Administración"]
        roles_in_db = db.query(Rol).filter(Rol.nombre.in_(collaborator_roles)).all()
        rol_map = {r.nombre: r for r in roles_in_db}
        rol_ids = [r.id for r in roles_in_db]

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

        # 1. Fetch active users by rol
        users = db.query(Usuario).filter(Usuario.rol_id.in_(rol_ids), Usuario.estado == True).all()
        users_by_rol = {}
        for u in users:
            users_by_rol.setdefault(u.rol_id, []).append(u)

        # 2. Fetch active tasks by rol (joined with Ruta)
        tasks = db.query(Tarea).join(Ruta).filter(Ruta.rol_id.in_(rol_ids), Tarea.estado == True).options(joinedload(Tarea.ruta)).all()
        tasks_by_rol = {}
        for t in tasks:
            tasks_by_rol.setdefault(t.ruta.rol_id, []).append(t)

        # 3. Fetch completed progresses for all active users and tasks
        all_user_ids = [u.id for u in users]
        all_task_ids = [t.id for t in tasks]
        completed_set = set()
        if all_user_ids and all_task_ids:
            completed_progs = db.query(Progreso.usuario_id, Progreso.tarea_id).filter(
                Progreso.usuario_id.in_(all_user_ids),
                Progreso.tarea_id.in_(all_task_ids),
                Progreso.estado == "Completado"
            ).all()
            completed_set = {(p_uid, p_tid) for p_uid, p_tid in completed_progs}

        # 4. Fetch latest activity for these users
        last_activity_map = {}
        if all_user_ids:
            latest_acts = db.query(Actividad.usuario_id, func.max(Actividad.created_at)).filter(
                Actividad.usuario_id.in_(all_user_ids)
            ).group_by(Actividad.usuario_id).all()
            last_activity_map = {uid: max_date for uid, max_date in latest_acts}

        # 5. Fetch fallback completed progresses (last completed task per user)
        last_progreso_map = {}
        if all_user_ids:
            latest_progs = db.query(Progreso.usuario_id, func.max(Progreso.fecha_completado)).filter(
                Progreso.usuario_id.in_(all_user_ids),
                Progreso.estado == "Completado"
            ).group_by(Progreso.usuario_id).all()
            last_progreso_map = {uid: max_date for uid, max_date in latest_progs}

        # 6. Fetch pending alerts count per user
        pending_alerts_count_map = {}
        if all_user_ids:
            alerts_counts = db.query(Alerta.usuario_id, func.count(Alerta.id)).filter(
                Alerta.usuario_id.in_(all_user_ids),
                Alerta.estado != "Atendida"
            ).group_by(Alerta.usuario_id).all()
            pending_alerts_count_map = {uid: cnt for uid, cnt in alerts_counts}

        res_details = []
        percentages = []

        for area_name in collaborator_roles:
            rol = rol_map.get(area_name)
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

            area_users = users_by_rol.get(rol.id, [])
            area_tasks = tasks_by_rol.get(rol.id, [])
            user_name = f"{area_users[0].nombre} {area_users[0].apellido}" if area_users else "Sin asignar"

            progress_val = 0
            if area_users and area_tasks:
                completed = sum(1 for u in area_users for t in area_tasks if (u.id, t.id) in completed_set)
                progress_val = round((completed / (len(area_users) * len(area_tasks))) * 100)

            percentages.append(progress_val)

            risk = "bajo"
            if progress_val < 50:
                risk = "alto"
            elif progress_val < 70:
                risk = "medio"

            # Last activity calculation
            last_act_str = "Sin actividad"
            if area_users:
                latest_dt = None
                for u in area_users:
                    act_dt = last_activity_map.get(u.id)
                    prog_dt = last_progreso_map.get(u.id)
                    if act_dt and (not latest_dt or act_dt > latest_dt):
                        latest_dt = act_dt
                    if prog_dt and (not latest_dt or prog_dt > latest_dt):
                        latest_dt = prog_dt
                if latest_dt:
                    last_act_str = format_time_diff(latest_dt)

            res_details.append({
                "area": area_name,
                "user": user_name,
                "progress": progress_val,
                "lastActivity": last_act_str,
                "risk": risk,
                "action": get_recommendation(area_name, progress_val),
                "color": colors.get(area_name, "#666666")
            })

        adopcion_global = round(sum(percentages) / len(percentages)) if percentages else 0

        # Areas in risk count calculation
        areas_riesgo_count = 0
        for idx, area_name in enumerate(collaborator_roles):
            p = percentages[idx]
            if p < 50:
                areas_riesgo_count += 1
                continue
            rol = rol_map.get(area_name)
            if rol:
                area_users = users_by_rol.get(rol.id, [])
                if area_users:
                    has_pending_alerts = any(pending_alerts_count_map.get(u.id, 0) > 0 for u in area_users)
                    if has_pending_alerts:
                        areas_riesgo_count += 1

        return res_details, adopcion_global, areas_riesgo_count

def fetch_active_users_data() -> tuple:
    with SessionLocal() as db:
        time_24h = datetime.utcnow() - timedelta(hours=24)
        activos_ids = db.query(Actividad.usuario_id).filter(Actividad.created_at >= time_24h).distinct().all()
        uids = [uid[0] for uid in activos_ids]
        total_users = db.query(Usuario).filter(Usuario.estado == True).count()
        
        active_areas = set()
        if uids:
            active_user_models = db.query(Usuario).options(joinedload(Usuario.rol)).filter(Usuario.id.in_(uids)).all()
            for au in active_user_models:
                if au.rol:
                    active_areas.add(normalize_area_name(au.rol.nombre))
        active_areas_str = ", ".join(sorted(list(active_areas))) if active_areas else "Ninguna"
        return len(uids), total_users, active_areas_str

def fetch_tickets_abiertos() -> int:
    with SessionLocal() as db:
        return db.query(Soporte).filter(Soporte.estado.notin_(["Resuelto", "Cerrado"])).count()

@router.get("/responsable")
async def get_dashboard_responsable(
    current_user: Usuario = Depends(require_admin_or_responsable)
):
    """
    Retrieve real statistics for the internal responsible dashboard page.
    Only accessible by Admin or Responsable Interno. Optimized and parallelized.
    """
    # Run independent database requests concurrently
    res_details_task = asyncio.to_thread(fetch_dashboard_responsable_data)
    active_users_task = asyncio.to_thread(fetch_active_users_data)
    tickets_task = asyncio.to_thread(fetch_tickets_abiertos)

    (res_details, adopcion_global, areas_riesgo_count), (activos_count, total_users, active_areas_str), tickets_abiertos = await asyncio.gather(
        res_details_task, active_users_task, tickets_task
    )

    return {
        "adopcion_global": adopcion_global,
        "areas_riesgo_alto": areas_riesgo_count,
        "usuarios_activos": f"{activos_count}/{total_users}",
        "usuarios_activos_sub": active_areas_str,
        "tickets_abiertos": tickets_abiertos,
        "avance_areas_detalle": res_details
    }
