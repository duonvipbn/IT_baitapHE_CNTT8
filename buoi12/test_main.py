import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_01_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_02_create_student_success():
    payload = {"student_code": "SV100", "full_name": "Test A", "email": "a@gmail.com", "age": 20, "major": "SE", "gpa": 3.5}
    response = client.post("/api/students", json=payload)
    assert response.status_code == 201
    assert response.json()["student_code"] == "SV100"

def test_03_create_duplicate_code():
    payload = {"student_code": "SV100", "full_name": "A", "email": "a@gmail.com", "age": 20, "major": "IT", "gpa": 3.0}
    client.post("/api/students", json=payload)
    response = client.post("/api/students", json={"student_code": "SV100", "full_name": "B", "email": "b@gmail.com", "age": 20, "major": "IT", "gpa": 3.0})
    assert response.status_code == 400

def test_04_create_validation_error():
    payload = {"student_code": "SV101", "full_name": "C", "email": "invalid-email", "age": 10, "major": "IT", "gpa": 5.0}
    response = client.post("/api/students", json=payload)
    assert response.status_code == 422

def test_05_get_student_by_id():
    res = client.post("/api/students", json={"student_code": "SV102", "full_name": "D", "email": "d@gmail.com", "age": 22, "major": "CS", "gpa": 3.8})
    student_id = res.json()["id"]
    response = client.get(f"/api/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["full_name"] == "D"

def test_06_get_student_not_found():
    assert client.get("/api/students/999").status_code == 404

def test_07_update_student_success():
    res = client.post("/api/students", json={"student_code": "SV103", "full_name": "E", "email": "e@gmail.com", "age": 21, "major": "CS", "gpa": 3.0})
    student_id = res.json()["id"]
    response = client.put(f"/api/students/{student_id}", json={"full_name": "Updated E", "gpa": 3.9})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated E"

def test_08_update_student_not_found():
    assert client.put("/api/students/999", json={"full_name": "New"}).status_code == 404

def test_09_delete_student_success():
    res = client.post("/api/students", json={"student_code": "SV104", "full_name": "F", "email": "f@gmail.com", "age": 20, "major": "SE", "gpa": 3.1})
    student_id = res.json()["id"]
    assert client.delete(f"/api/students/{student_id}").status_code == 204
    assert client.get(f"/api/students/{student_id}").status_code == 404

def test_10_filter_by_major():
    client.post("/api/students", json={"student_code": "SV1", "full_name": "S1", "email": "s1@g.com", "age": 20, "major": "SE", "gpa": 3.0})
    client.post("/api/students", json={"student_code": "SV2", "full_name": "S2", "email": "s2@g.com", "age": 20, "major": "CS", "gpa": 3.0})
    res = client.get("/api/students?major=SE")
    assert res.status_code == 200 and res.json()["total"] == 1

def test_11_search_by_name():
    client.post("/api/students", json={"student_code": "SV105", "full_name": "Alpha", "email": "al@g.com", "age": 20, "major": "SE", "gpa": 3.0})
    res = client.get("/api/students?search=Alpha")
    assert res.status_code == 200 and res.json()["total"] == 1

def test_12_pagination():
    for i in range(5):
        client.post("/api/students", json={"student_code": f"SV20{i}", "full_name": f"S{i}", "email": f"s{i}@g.com", "age": 20, "major": "IT", "gpa": 3.0})
    res = client.get("/api/students?page=1&limit=2")
    assert res.status_code == 200 and len(res.json()["data"]) == 2