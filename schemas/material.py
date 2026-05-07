from pydantic import BaseModel, Field


class MaterialCreate(BaseModel):
    name: str
    lead_time_days: int = Field(..., ge=0)
    phase_id: int


class MaterialUpdate(BaseModel):
    name: str | None = None
    lead_time_days: int | None = Field(default=None, ge=0)
    phase_id: int | None = None


class MaterialOut(BaseModel):
    id: int
    name: str
    lead_time_days: int
    phase_id: int

    class Config:
        orm_mode = True
