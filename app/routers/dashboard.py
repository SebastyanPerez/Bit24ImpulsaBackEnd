from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.usuarios import Usuario

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
def get_dashboard_data(current_user: Usuario = Depends(get_current_user)):
    """Protected dashboard endpoint returning mocked statistics."""
    return {
        "message": f"Welcome to the dashboard, user {current_user.correo}!",
        "metrics": {
            "usuarios_activos": 42,
            "tareas_pendientes": 5,
            "progreso_general_porcentaje": 75.4,
            "alertas_criticas": 1
        },
        "notificaciones": [
            {"id": 1, "mensaje": "Nueva ruta asignada", "leido": False},
            {"id": 2, "mensaje": "Soporte técnico respondió a tu solicitud", "leido": True}
        ]
    }
