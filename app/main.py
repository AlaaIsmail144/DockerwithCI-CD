from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Student


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # ينشئ الجدول تلقائياً لو مش موجود
    yield


app = FastAPI(title="Students API", lifespan=lifespan)


class StudentIn(BaseModel):
    name: str


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/students", response_model=list[StudentOut])
def list_students(db: Session = Depends(get_db)):
    return db.scalars(select(Student)).all()


@app.post("/students", response_model=StudentOut, status_code=201)
def create_student(payload: StudentIn, db: Session = Depends(get_db)):
    student = Student(name=payload.name)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student