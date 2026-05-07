from sqlalchemy import Column, Integer, String
from app.database import Base

class Phase(Base):
    __tablename__ = "phases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False, unique=True)
    duration_days = Column(Integer, nullable=False)
