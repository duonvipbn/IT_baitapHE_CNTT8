from typing import List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

db: List[dict] = []

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

class StudentCreate(BaseModel):
    student_code: str = Field(..., min_length=1, strip_whitespace=True)
    full_name: str = Field(..., min_length=1, strip_whitespace=True)
    email: str = Field(..., pattern=EMAIL_REGEX)
    age: int = Field(..., ge=18, le=60)
    is_active: bool = True


@app.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate):
    for item in db:
        if item["student_code"] == student.student_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student code already exists"
            )
        if item["email"] == student.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    student_data = student.model_dump()
    db.append(student_data)
    return student_data