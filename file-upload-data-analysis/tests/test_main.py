import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the File Processing System"}

def test_upload_pdf():
    with open("test_files/test.pdf", "rb") as f:
        response = client.post("/upload/", files={"files": ("test.pdf", f, "application/pdf")})
    assert response.status_code == 200
    assert "filename" in response.json()[0]
    assert "form" in response.json()[0]

def test_upload_xlsx():
    with open("test_files/test.xlsx", "rb") as f:
        response = client.post("/upload/", files={"files": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert response.status_code == 200
    assert "filename" in response.json()[0]
    assert "form" in response.json()[0]

def test_upload_cad():
    with open("test_files/test.dwg", "rb") as f:
        response = client.post("/upload/", files={"files": ("test.dwg", f, "application/acad")})
    assert response.status_code == 200
    assert "filename" in response.json()[0]
    assert "form" in response.json()[0]

def test_upload_unsupported_file():
    with open("test_files/test.txt", "rb") as f:
        response = client.post("/upload/", files={"files": ("test.txt", f, "text/plain")})
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

# Add more tests for other endpoints and edge cases