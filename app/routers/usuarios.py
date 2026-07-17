import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.core.dependencies import require_admin, require_admin_or_responsable
from app.core.security import hash_password
from app.models.usuarios import Usuario
from app.models.roles import Rol
from app.schemas.usuario import UsuarioOut, UsuarioCreate, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _get_usuario(db: Session, usuario_id: uuid.UUID) -> Usuario | None:
    return (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(Usuario.id == usuario_id)
        .first()
    )


def _ensure_correo_disponible(db: Session, correo: str, usuario_id: uuid.UUID | None = None) -> None:
    query = db.query(Usuario).filter(Usuario.correo == correo)
    if usuario_id is not None:
        query = query.filter(Usuario.id != usuario_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado",
        )


def _ensure_rol_existe(db: Session, rol_id: uuid.UUID) -> None:
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol especificado no existe",
        )


@router.get("", response_model=List[UsuarioOut])
def list_usuarios(db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin_or_responsable)):
    """List all users."""
    return db.query(Usuario).options(joinedload(Usuario.rol)).all()


@router.get("/{usuario_id}", response_model=UsuarioOut)
def get_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    """Get a user by ID."""
    usuario = _get_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return usuario


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def create_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    """Create a new user. The password is hashed before saving."""
    _ensure_correo_disponible(db, usuario_data.correo)

    if usuario_data.rol_id:
        _ensure_rol_existe(db, usuario_data.rol_id)

    new_user = Usuario(
        nombre=usuario_data.nombre,
        apellido=usuario_data.apellido,
        correo=usuario_data.correo,
        password_hash=hash_password(usuario_data.password),
        rol_id=usuario_data.rol_id,
        estado=True,
    )
    db.add(new_user)
    db.commit()

    usuario = _get_usuario(db, new_user.id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el usuario creado",
        )
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioOut)
def update_usuario(usuario_id: uuid.UUID, usuario_data: UsuarioUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    """Update an existing user without modifying the password."""
    usuario = _get_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    if usuario_data.correo is not None and usuario_data.correo != usuario.correo:
        _ensure_correo_disponible(db, usuario_data.correo, usuario_id)

    if usuario_data.rol_id is not None:
        _ensure_rol_existe(db, usuario_data.rol_id)

    if usuario_data.nombre is not None:
        usuario.nombre = usuario_data.nombre
    if usuario_data.apellido is not None:
        usuario.apellido = usuario_data.apellido
    if usuario_data.correo is not None:
        usuario.correo = usuario_data.correo
    if usuario_data.rol_id is not None:
        usuario.rol_id = usuario_data.rol_id
    if usuario_data.estado is not None:
        usuario.estado = usuario_data.estado
    if usuario_data.password is not None and usuario_data.password.strip() != "":
        if len(usuario_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 8 caracteres",
            )
        usuario.password_hash = hash_password(usuario_data.password)

    db.commit()

    usuario = _get_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return usuario


@router.delete("/{usuario_id}", response_model=UsuarioOut)
def delete_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    """Soft delete user by setting status (estado) to False."""
    usuario = _get_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    usuario.estado = False
    db.commit()

    usuario = _get_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return usuario
