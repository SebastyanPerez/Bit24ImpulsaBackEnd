from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
    # Search user by email (correo)
    user = db.query(Usuario).filter(Usuario.correo == login_data.correo).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token using user UUID as string in subject (sub)
    token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": user
    }

@router.get("/me", response_model=UsuarioOut)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """Get profile of the currently logged in user."""
    return current_user
