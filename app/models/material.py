from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    phase_id = Column(Integer, ForeignKey("phases.id"))

    def __init__(self, id=None, name=None, lead_time_days=None, phase_id=None):
        self.id = id
        self.name = name
        self.lead_time_days = lead_time_days
        self.phase_id = phase_id
