from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Student Management API")

db_students = [
    {"id": 1, "name": "Nguyễn Văn A", "email": "a.nguyen@gmail.com", "age": 20},
    {"id": 2, "name": "Trần Thị B", "email": "b.tran@gmail.com", "age": 21},
]

current_id = 2


class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    age: int


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int


def find_student_by_id(student_id: int):
    for student in db_students:
        if student["id"] == student_id:
            return student
    return None


def is_email_taken(email: str, exclude_id: Optional[int] = None) -> bool:
    for student in db_students:
        if student["email"] == email and student["id"] != exclude_id:
            return True
    return False


@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student(student: StudentCreate):
    global current_id

    if is_email_taken(student.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã tồn tại trong hệ thống.",
        )

    current_id += 1
    new_student = {
        "id": current_id,
        "name": student.name,
        "email": student.email,
        "age": student.age,
    }
    db_students.append(new_student)
    return new_student


@app.get("/students", response_model=List[StudentResponse])
def get_all_students():
    return db_students


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student_by_id(student_id: int):
    student = find_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID = {student_id}",
        )
    return student


@app.patch("/students/{student_id}", response_model=StudentResponse)
@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_data: StudentUpdate):
    student = find_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không thể cập nhật. Không tìm thấy sinh viên có ID = {student_id}",
        )

    if (
        student_data.email
        and is_email_taken(student_data.email, exclude_id=student_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email cập nhật đã trùng với sinh viên khác.",
        )

    update_dict = student_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        student[key] = value

    return student


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    student = find_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không thể xóa. Không tìm thấy sinh viên có ID = {student_id}",
        )

    db_students.remove(student)
    return {"message": f"Đã xóa thành công sinh viên có ID = {student_id}"}
