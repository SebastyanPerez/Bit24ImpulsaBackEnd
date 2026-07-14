import os
import sys
import uuid

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.usuarios import Usuario
from app.models.categorias_soporte import CategoriaSoporte
from app.models.soporte import Soporte
from app.core.dependencies import get_current_user, require_admin_or_responsable

# Mock dependencies to return test admin/user
class MockRol:
    def __init__(self, nombre):
        self.id = uuid.uuid4()
        self.nombre = nombre

class MockUser:
    def __init__(self, id, correo, rol_nombre):
        self.id = id
        self.correo = correo
        self.rol = MockRol(rol_nombre)

# Locate first normal user and admin in the DB to test with real users
db = SessionLocal()
try:
    first_user = db.query(Usuario).first()
    if not first_user:
        print("Warning: No users found in database to carry out tests.")
        sys.exit(0)
    
    # We find a category to use
    category = db.query(CategoriaSoporte).first()
    if not category:
        print("Warning: No categories found in database to carry out tests.")
        sys.exit(0)

    print(f"Testing with User: {first_user.nombre} {first_user.apellido} ({first_user.id})")
    print(f"Testing with Category: {category.nombre} ({category.id})")

    # Mocks
    mock_regular_user = MockUser(first_user.id, first_user.correo, "Ventas")
    mock_admin_user = MockUser(first_user.id, first_user.correo, "Administrador")

    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_regular_user
    app.dependency_overrides[require_admin_or_responsable] = lambda: mock_admin_user

    client = TestClient(app)

    # 1. GET /categorias-soporte
    print("\n--- 1. Testing GET /categorias-soporte ---")
    res = client.get("/categorias-soporte")
    print("Status:", res.status_code)
    categories_list = res.json()
    print("Categories returned:", [c["nombre"] for c in categories_list])
    assert res.status_code == 200
    assert len(categories_list) > 0

    # 2. POST /soporte
    print("\n--- 2. Testing POST /soporte ---")
    payload = {
        "categoria_id": str(category.id),
        "titulo": "Ticket de prueba",
        "descripcion": "Descripción larga de prueba para el ticket de soporte."
    }
    res = client.post("/soporte", json=payload)
    print("Status:", res.status_code)
    ticket = res.json()
    print("Created Ticket ID:", ticket["id"], "Estado:", ticket["estado"])
    assert res.status_code == 201
    assert ticket["estado"] == "Abierto"
    assert ticket["titulo"] == "Ticket de prueba"
    ticket_id = ticket["id"]

    # 3. GET /soporte/me
    print("\n--- 3. Testing GET /soporte/me ---")
    res = client.get("/soporte/me")
    print("Status:", res.status_code)
    my_tickets = res.json()
    print("My tickets count:", len(my_tickets))
    assert res.status_code == 200
    assert any(t["id"] == ticket_id for t in my_tickets)

    # 4. GET /soporte (Admin)
    print("\n--- 4. Testing GET /soporte ---")
    res = client.get("/soporte")
    print("Status:", res.status_code)
    all_tickets = res.json()
    print("All tickets count:", len(all_tickets))
    assert res.status_code == 200
    assert any(t["id"] == ticket_id for t in all_tickets)

    # 5. PUT /soporte/{id}/asignar
    print("\n--- 5. Testing PUT /soporte/{id}/asignar ---")
    assign_payload = {
        "responsable_id": str(first_user.id)
    }
    res = client.put(f"/soporte/{ticket_id}/asignar", json=assign_payload)
    print("Status:", res.status_code)
    assigned_ticket = res.json()
    print("Assigned ticket - Resp ID:", assigned_ticket["responsable_id"], "Estado:", assigned_ticket["estado"])
    assert res.status_code == 200
    assert assigned_ticket["estado"] == "En Proceso"
    assert assigned_ticket["responsable_id"] == str(first_user.id)

    # 6. PUT /soporte/{id}/estado
    print("\n--- 6. Testing PUT /soporte/{id}/estado ---")
    status_payload = {
        "estado": "Resuelto"
    }
    res = client.put(f"/soporte/{ticket_id}/estado", json=status_payload)
    print("Status:", res.status_code)
    resolved_ticket = res.json()
    print("Updated ticket - Estado:", resolved_ticket["estado"])
    assert res.status_code == 200
    assert resolved_ticket["estado"] == "Resuelto"

    # Cleaning up
    print("\n--- Cleaning up test ticket ---")
    db_ticket = db.query(Soporte).filter(Soporte.id == uuid.UUID(ticket_id)).first()
    if db_ticket:
        db.delete(db_ticket)
        db.commit()
    print("Cleanup successful.")

except Exception as e:
    print("Error during test execution:", e)
    sys.exit(1)
finally:
    db.close()

print("\n--- Verification Completed Successfully! ---")
