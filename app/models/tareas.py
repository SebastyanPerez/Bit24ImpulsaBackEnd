from sqlalchemy import Column, Integer
from app.database import Base

class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
