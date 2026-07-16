from sqlalchemy import Column, Integer
from app.database import Base

class IntegracionBit24(Base):
    __tablename__ = "integracion_bit24"

    id = Column(Integer, primary_key=True, index=True)
