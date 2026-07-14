from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.routers import auth, dashboard, usuarios, roles, rutas, tareas, guias, progreso

from app.config import settings

app = FastAPI(
    title="Bit24 Impulsa API",
    description="Backend API for the Bit24 Impulsa project.",
    version="1.0.0"
)

# CORS configuration
origins = [o.strip() for o in settings.allowed_origins.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(usuarios.router)
app.include_router(roles.router)
app.include_router(rutas.router)
app.include_router(tareas.router)
app.include_router(guias.router)
app.include_router(progreso.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Bit24 Impulsa API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Execute a simple query to verify database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        err_msg = "Unknown database error"
        if hasattr(e, 'args') and e.args:
            parts = []
            for arg in e.args:
                if isinstance(arg, bytes):
                    parts.append(arg.decode('utf-8', errors='replace'))
                elif isinstance(arg, str):
                    parts.append(arg)
                else:
                    parts.append(repr(arg))
            err_msg = " | ".join(parts)
        else:
            try:
                err_msg = repr(e)
            except Exception:
                err_msg = e.__class__.__name__
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {err_msg}"
        )
