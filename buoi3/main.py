from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

students_db = [
    {"id": 1, "name": "Nguyen Van A", "age": 20},
    {"id": 2, "name": "Tran Thi B", "age": 22},
    {"id": 3, "name": "Le Van C", "age": 19},
    {"id": 4, "name": "Pham Minh D", "age": 25},
    {"id": 5, "name": "Hoang Anh E", "age": 18}
]

class StudentResponse(BaseModel):
    id: int
    name: str
    age: int

@app.get("/")
def read_root():
    return {"message": "Welcome to Student Management System"}

@app.get("/students", response_model=List[StudentResponse])
def get_all_students():
    return students_db

@app.get("/students/search", response_model=List[StudentResponse])
def search_students(keyword: str = ""):
    if not keyword:
        return students_db
    kw = keyword.lower()
    return [s for s in students_db if kw in s["name"].lower()]

@app.get("/students/filter", response_model=List[StudentResponse])
def filter_students_by_age(max_age: Optional[int] = Query(None, ge=0)):
    if max_age is None:
        return students_db
    return [s for s in students_db if s["age"] <= max_age]

@app.get("/students/{id}", response_model=StudentResponse)
def get_student_by_id(id: int):
    for s in students_db:
        if s["id"] == id:
            return s
    raise HTTPException(status_code=404, detail="Student not found")