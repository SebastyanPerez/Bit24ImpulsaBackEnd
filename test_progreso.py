import os
import sys
import uuid

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.routers.progreso import get_progreso_me, get_progreso_resumen

class MockRol:
    id = uuid.UUID("d0a1624b-1b71-4f25-86b6-4f86cc141b47")
    nombre = "Administrador"

class MockUser:
    id = uuid.UUID("18409fba-8014-4270-9a37-8c58fbf0a34e")
    correo = "admin@bit24.com"
    rol = MockRol()

mock_user = MockUser()

db = SessionLocal()
try:
    print("--- Testing get_progreso_me handler ---")
    results = get_progreso_me(db=db, current_user=mock_user)
    print("Record count:", len(results))
    for r in results[:2]:
        print("Progress ID:", r.id, "Estado:", r.estado, "Tarea:", r.tarea.titulo)

    print("\n--- Testing get_progreso_resumen handler ---")
    resumen = get_progreso_resumen(db=db, current_user=mock_user)
    for res in resumen:
        print(f"Rol: {res['rol_nombre']} - Adopción: {res['porcentaje_adopcion']}% "
              f"(Completadas: {res['tareas_completadas']}, Activas: {res['tareas_activas']}, Usuarios: {res['usuarios_activos']})")
finally:
    db.close()

print("\n--- Verification Completed Successfully! ---")
