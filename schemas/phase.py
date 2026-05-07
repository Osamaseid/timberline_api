from pydantic import BaseModel, Field


class PhaseCreate(BaseModel):
    name: str
    order: int = Field(..., ge=1)
    duration_days: int = Field(..., ge=1)


class PhaseUpdate(BaseModel):
    name: str | None = None
    order: int | None = Field(default=None, ge=1)
    duration_days: int | None = Field(default=None, ge=1)


class PhaseOut(BaseModel):
    id: int
    name: str
    order: int
    duration_days: int

    class Config:
        orm_mode = True
