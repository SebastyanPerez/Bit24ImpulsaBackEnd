from sqlalchemy import Column, Integer
from app.database import Base

class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
