from sqlalchemy import Column, Integer
from app.database import Base

class CategoriaSoporte(Base):
    __tablename__ = "categorias_soporte"

    id = Column(Integer, primary_key=True, index=True)
