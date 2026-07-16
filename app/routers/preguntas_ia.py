import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.usuarios import Usuario
from app.models.preguntas_ia import PreguntaIA
from app.core.gemini_client import preguntar_ia
from app.schemas.preguntas_ia import PreguntaCreate, PreguntaOut

router = APIRouter(prefix="/asistente-ia", tags=["asistente-ia"])

@router.post("", response_model=PreguntaOut, status_code=status.HTTP_201_CREATED)
async def crear_pregunta_ia(
    pregunta_in: PreguntaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Submit a question to the AI assistant.
    Calls Gemini API to retrieve answer & category, and logs it in the database.
    """
    res_ai = await preguntar_ia(pregunta_in.pregunta)
    
    db_pregunta = PreguntaIA(
        usuario_id=current_user.id,
        tarea_id=pregunta_in.tarea_id,
        guia_id=pregunta_in.guia_id,
        pregunta=pregunta_in.pregunta,
        respuesta=res_ai["respuesta"],
        categoria=res_ai["categoria"]
    )
    
    db.add(db_pregunta)
    db.commit()
    db.refresh(db_pregunta)

    from app.core.actividad_service import registrar_actividad
    registrar_actividad(
        db,
        current_user.id,
        "IA",
        "Consultó al asistente IA",
        detalle=pregunta_in.pregunta[:100]
    )
    
    return db_pregunta

@router.get("/historial", response_model=List[PreguntaOut])
def get_historial_ia(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retrieve the last 20 queries asked by the authenticated user, sorted by created_at descending.
    """
    return (
        db.query(PreguntaIA)
        .filter(PreguntaIA.usuario_id == current_user.id)
        .order_by(PreguntaIA.created_at.desc())
        .limit(20)
        .all()
    )
