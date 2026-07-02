from sqlalchemy import Column, Integer
from app.database import Base

class Progreso(Base):
    __tablename__ = "progreso"

    id = Column(Integer, primary_key=True, index=True)
