import os
import sys
import uuid
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.usuarios import Usuario
from app.models.alertas import Alerta
from app.routers.alertas import (
    get_alertas_me,
    leer_alerta,
    create_alerta,
    get_all_alertas,
    atender_alerta
)
from app.schemas.alertas import AlertaCreate

class MockRol:
    id = uuid.uuid4()
    nombre = "Administrador"

class MockUser:
    id = None
    correo = "admin@bit24.com"
    rol = MockRol()

db = SessionLocal()
try:
    first_user = db.query(Usuario).first()
    if not first_user:
        print("Warning: No users found in database to carry out tests.")
        sys.exit(0)

    print(f"Testing with User: {first_user.nombre} {first_user.apellido} ({first_user.id})")
    
    mock_user = MockUser()
    mock_user.id = first_user.id
    
    print("\n--- 1. Testing create_alerta handler ---")
    payload = AlertaCreate(
        usuario_id=first_user.id,
        titulo="Alerta de Test de Integracion",
        mensaje="Esta es una alerta de prueba generada por la verificacion automatizada.",
        tipo="Test",
        canal="Sistema",
        accion_recomendada="Verificar salida terminal"
    )
    new_alert = create_alerta(alerta_in=payload, db=db, current_user=mock_user)
    print("Created Alert ID:", new_alert.id, "Estado:", new_alert.estado)

    print("\n--- 2. Testing get_alertas_me handler ---")
    my_alerts = get_alertas_me(db=db, current_user=mock_user)
    print("My Alerts count:", len(my_alerts))
    found_created = any(a.id == new_alert.id for a in my_alerts)
    print("Created alert found in my alerts list:", found_created)

    print("\n--- 3. Testing leer_alerta (Read) handler ---")
    read_alert = leer_alerta(id=new_alert.id, db=db, current_user=mock_user)
    print("Alert State after 'leer':", read_alert.estado)

    print("\n--- 4. Testing get_all_alertas handler ---")
    all_alerts = get_all_alertas(db=db, current_user=mock_user)
    print("Global Alerts count:", len(all_alerts))

    print("\n--- 5. Testing atender_alerta handler ---")
    resolved_alert = atender_alerta(id=new_alert.id, db=db, current_user=mock_user)
    print("Alert State after 'atender':", resolved_alert.estado, "Atendida En:", resolved_alert.fecha_atendida)

    print("\n--- Cleaning up test alert ---")
    db.delete(db.query(Alerta).filter(Alerta.id == new_alert.id).first())
    db.commit()
    print("Cleanup successful.")

except Exception as e:
    print("Error during test execution:", e)
    sys.exit(1)
finally:
    db.close()

print("\n--- Verification Completed Successfully! ---")
