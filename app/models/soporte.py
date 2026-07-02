from sqlalchemy import Column, Integer
from app.database import Base

class Soporte(Base):
    __tablename__ = "soporte"

    id = Column(Integer, primary_key=True, index=True)
