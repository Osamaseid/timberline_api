from fastapi import FastAPI

from app.database import Base, engine
from routers import material, phase, project

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Timberline & Trestle Scheduling API")

app.include_router(phase.router)
app.include_router(material.router)
app.include_router(project.router)
