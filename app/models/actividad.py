from sqlalchemy import Column, Integer
from app.database import Base

class Actividad(Base):
    __tablename__ = "actividades"

    id = Column(Integer, primary_key=True, index=True)
