from sqlalchemy import Column, Integer
from app.database import Base

class Guia(Base):
    __tablename__ = "guias"

    id = Column(Integer, primary_key=True, index=True)
