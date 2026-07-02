from sqlalchemy import Column, Integer
from app.database import Base

class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
