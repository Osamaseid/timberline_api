from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.material import Material
from app.models.phase import Phase
from schemas.material import MaterialCreate, MaterialOut, MaterialUpdate

router = APIRouter(prefix="/materials", tags=["Materials"])


def _get_or_404(material_id: int, db: Session) -> Material:
    material = db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found.")
    return material


def _validate_phase(phase_id: int, db: Session) -> None:
    if not db.get(Phase, phase_id):
        raise HTTPException(status_code=404, detail=f"Phase {phase_id} not found.")


@router.post("/", response_model=MaterialOut, status_code=201)
def create_material(payload: MaterialCreate, db: Session = Depends(get_db)) -> Material:
    _validate_phase(payload.phase_id, db)
    material = Material(**payload.model_dump())
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.get("/", response_model=list[MaterialOut])
def list_materials(db: Session = Depends(get_db)) -> list[Material]:
    return db.query(Material).all()


@router.get("/{material_id}", response_model=MaterialOut)
def get_material(material_id: int, db: Session = Depends(get_db)) -> Material:
    return _get_or_404(material_id, db)


@router.put("/{material_id}", response_model=MaterialOut)
def update_material(
    material_id: int, payload: MaterialUpdate, db: Session = Depends(get_db)
) -> Material:
    material = _get_or_404(material_id, db)
    if payload.phase_id is not None:
        _validate_phase(payload.phase_id, db)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(material, field, value)
    db.commit()
    db.refresh(material)
    return material


@router.delete("/{material_id}", status_code=204)
def delete_material(material_id: int, db: Session = Depends(get_db)) -> None:
    material = _get_or_404(material_id, db)
    db.delete(material)
    db.commit()
