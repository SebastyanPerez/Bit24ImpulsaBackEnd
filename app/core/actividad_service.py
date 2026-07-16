import sys
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.actividad import Actividad

def registrar_actividad(
    db: Session,
    usuario_id: uuid.UUID,
    modulo: str,
    accion: str,
    referencia_id: Optional[uuid.UUID] = None,
    detalle: Optional[str] = None
) -> None:
    """
    Inserts a row into the 'actividad' table.
    Wraps the write within a nested transaction (savepoint) to avoid
    disrupting the main transaction of the calling endpoint.
    If writing to the log fails, exceptions are suppressed and logged to stderr.
    """
    try:
        with db.begin_nested():
            db_actividad = Actividad(
                usuario_id=usuario_id,
                modulo=modulo,
                accion=accion,
                referencia_id=referencia_id,
                detalle=detalle
            )
            db.add(db_actividad)
        db.commit()
    except Exception as e:
        # Prevent logging library error from crashing main request thread
        print(f"Error al registrar actividad: {e}", file=sys.stderr)
