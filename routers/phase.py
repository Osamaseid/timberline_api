from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.phase import Phase
from schemas.phase import PhaseCreate, PhaseOut, PhaseUpdate

router = APIRouter(prefix="/phases", tags=["Phases"])


def _get_or_404(phase_id: int, db: Session) -> Phase:
    phase = db.get(Phase, phase_id)
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found.")
    return phase


@router.post("/", response_model=PhaseOut, status_code=201)
def create_phase(payload: PhaseCreate, db: Session = Depends(get_db)) -> Phase:
    if db.query(Phase).filter(Phase.order == payload.order).first():
        raise HTTPException(status_code=400, detail="Phase order must be unique.")
    phase = Phase(**payload.model_dump())
    db.add(phase)
    db.commit()
    db.refresh(phase)
    return phase


@router.get("/", response_model=list[PhaseOut])
def list_phases(db: Session = Depends(get_db)) -> list[Phase]:
    return db.query(Phase).order_by(Phase.order).all()


@router.get("/{phase_id}", response_model=PhaseOut)
def get_phase(phase_id: int, db: Session = Depends(get_db)) -> Phase:
    return _get_or_404(phase_id, db)


@router.put("/{phase_id}", response_model=PhaseOut)
def update_phase(
    phase_id: int, payload: PhaseUpdate, db: Session = Depends(get_db)
) -> Phase:
    phase = _get_or_404(phase_id, db)
    if payload.order is not None and payload.order != phase.order:
        if db.query(Phase).filter(Phase.order == payload.order).first():
            raise HTTPException(status_code=400, detail="Phase order must be unique.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(phase, field, value)
    db.commit()
    db.refresh(phase)
    return phase


@router.delete("/{phase_id}", status_code=204)
def delete_phase(phase_id: int, db: Session = Depends(get_db)) -> None:
    phase = _get_or_404(phase_id, db)
    db.delete(phase)
    db.commit()
