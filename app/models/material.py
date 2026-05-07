from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    phase_id = Column(Integer, ForeignKey("phases.id"))
