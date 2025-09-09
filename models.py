from sqlalchemy import Column, Integer, String
from database import Base

class Quarto(Base):
    __tablename__ = "quartos"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True)
    tipo = Column(String)
    valor = Column(Integer)
    disponivel = Column(String)