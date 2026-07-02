import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import require_admin
from app.core.security import hash_password
from app.models.usuarios import Usuario
from app.models.roles import Rol
from app.schemas.usuario import UsuarioOut, UsuarioCreate, UsuarioUpdate

# Instantiate router and enforce require_admin dependency for all endpoints
router = APIRouter(prefix="/usuarios", tags=["usuarios"], dependencies=[Depends(require_admin)])

@router.get("", response_model=List[UsuarioOut])
def list_usuarios(db: Session = Depends(get_db)):
    """List all users."""
    return db.query(Usuario).all()

@router.get("/{usuario_id}", response_model=UsuarioOut)
def get_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a user by ID."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario

@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def create_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """Create a new user. The password is hashed before saving."""
    # Check if email is already taken
    existing_user = db.query(Usuario).filter(Usuario.correo == usuario_data.correo).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )
    
    # Check if rol_id exists if provided
    if usuario_data.rol_id:
        rol = db.query(Rol).filter(Rol.id == usuario_data.rol_id).first()
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El rol especificado no existe"
            )

    # Hash the password
    hashed_pwd = hash_password(usuario_data.password)
    
    # Create the user
    new_user = Usuario(
        nombre=usuario_data.nombre,
        apellido=usuario_data.apellido,
        correo=usuario_data.correo,
        password_hash=hashed_pwd,
        rol_id=usuario_data.rol_id,
        estado=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/{usuario_id}", response_model=UsuarioOut)
def update_usuario(usuario_id: uuid.UUID, usuario_data: UsuarioUpdate, db: Session = Depends(get_db)):
    """Update an existing user. Optional password will be hashed if provided."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Check if email is being updated to an already existing one
    if usuario_data.correo and usuario_data.correo != usuario.correo:
        existing_user = db.query(Usuario).filter(Usuario.correo == usuario_data.correo).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado"
            )
            
    # Check if rol_id exists if provided
    if usuario_data.rol_id:
        rol = db.query(Rol).filter(Rol.id == usuario_data.rol_id).first()
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El rol especificado no existe"
            )

    # Update fields if they are provided
    if usuario_data.nombre is not None:
        usuario.nombre = usuario_data.nombre
    if usuario_data.apellido is not None:
        usuario.apellido = usuario_data.apellido
    if usuario_data.correo is not None:
        usuario.correo = usuario_data.correo
    if usuario_data.rol_id is not None:
        usuario.rol_id = usuario_data.rol_id
        
    # Hash and update password if provided
    if usuario_data.password is not None:
        usuario.password_hash = hash_password(usuario_data.password)

    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/{usuario_id}", response_model=UsuarioOut)
def delete_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    """Soft delete user by setting status (estado) to False."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
        
    usuario.estado = False
    db.commit()
    db.refresh(usuario)
    return usuario
