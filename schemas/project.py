from datetime import datetime
from pydantic import BaseModel

from schemas.phase import PhaseOut


class PhaseMilestone(BaseModel):
    phase: PhaseOut
    earliest_start_date: datetime


class ScheduleResponse(BaseModel):
    desired_start: datetime
    earliest_safe_start: datetime
    delay_days: int
    milestones: list[PhaseMilestone]
