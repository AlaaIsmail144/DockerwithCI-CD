import os

# لازم قبل أي import من app، لأن config.py بيقرا المتغيرات دي وقت الـ import
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

# داتابيز SQLite في الذاكرة (بتتمسح أول ما الاختبار يخلص)
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


# "في الاختبار، استخدم SQLite بدل Postgres"
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_list_student():
    response = client.post("/students", json={"name": "Mona"})
    assert response.status_code == 201
    assert response.json()["name"] == "Mona"

    response = client.get("/students")
    assert response.status_code == 200
    names = [s["name"] for s in response.json()]
    assert "Mona" in names

def test_create_student_without_name_fails():
    response = client.post("/students", json={})
    assert response.status_code == 422  # التحقق التلقائي من Pydantic