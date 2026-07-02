from sqlalchemy import Column, Integer
from app.database import Base

class PreguntaIA(Base):
    __tablename__ = "preguntas_ia"

    id = Column(Integer, primary_key=True, index=True)
