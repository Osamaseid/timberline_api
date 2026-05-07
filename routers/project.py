from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.material import Material
from app.models.phase import Phase
from schemas.phase import PhaseOut
from schemas.project import PhaseMilestone, ScheduleResponse
from services.scheduler import calculate_earliest_start
from utils.exceptions import SchedulingError

router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.get("/", response_model=ScheduleResponse)
def get_schedule(
    desired_start: datetime = Query(default_factory=datetime.utcnow),
    db: Session = Depends(get_db),
) -> ScheduleResponse:
    materials = db.query(Material).all()
    phases = db.query(Phase).order_by(Phase.order).all()

    try:
        earliest_safe_start = calculate_earliest_start(materials, phases, desired_start)
    except SchedulingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    delay_days = (earliest_safe_start - desired_start).days

    # Build per-phase milestones: each phase starts after all preceding phases complete.
    milestones: list[PhaseMilestone] = []
    cursor = earliest_safe_start
    for phase in phases:
        milestones.append(
            PhaseMilestone(phase=PhaseOut.from_orm(phase), earliest_start_date=cursor)
        )
        cursor += timedelta(days=phase.duration_days)

    return ScheduleResponse(
        desired_start=desired_start,
        earliest_safe_start=earliest_safe_start,
        delay_days=delay_days,
        milestones=milestones,
    )
