from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.schemas.auth import UsuarioLogin, Token
from app.schemas.usuario import UsuarioOut
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, verify_password
from app.models.usuarios import Usuario

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(login_data: UsuarioLogin, db: Session = Depends(get_db)):
    """Authenticate user, verify password, and return a JWT access token."""
    user = (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(Usuario.correo == login_data.correo)
        .first()
    )

    is_valid = True
    if not user:
        is_valid = False
        # Avoid user enumeration via timing attack
        verify_password(login_data.password, "$2b$12$0123456789abcdefjhijk.lmnopqrstuvwxyzABCDEFGHIJKLM")
    else:
        if not verify_password(login_data.password, user.password_hash):
            is_valid = False
        if not user.estado:
            is_valid = False

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": str(user.id)}
    if user.rol:
        token_data["rol"] = user.rol.nombre

    token = create_access_token(data=token_data)

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": user
    }


@router.get("/me", response_model=UsuarioOut)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """Get profile of the currently logged in user."""
    return current_user
