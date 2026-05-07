from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from app.database import Base

class Phase(Base):
    __tablename__ = "phases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False, unique=True)
    duration_days = Column(Integer, nullable=False)

    def __init__(self, id=None, name=None, order=None, duration_days=None):
        self.id = id
        self.name = name
        self.order = order
        self.duration_days = duration_days
