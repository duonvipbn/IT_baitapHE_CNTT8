import os
from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func, or_, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_USER: str = "root"
    DB_PASSWORD: str = "19112006"
    DB_NAME: str = "connect_db"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_code = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    major = Column(String(50), nullable=False)
    gpa = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

Base.metadata.create_all(bind=engine)

class StudentBase(BaseModel):
    student_code: str = Field(..., min_length=3, max_length=20)
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=16, le=100)
    major: str = Field(..., min_length=2, max_length=50)
    gpa: float = Field(default=0.0, ge=0.0, le=4.0)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=16, le=100)
    major: Optional[str] = Field(None, min_length=2, max_length=50)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class PaginatedStudentResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[StudentResponse]

app = FastAPI(title="Student Management API")

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database failed: {str(e)}")

@app.post("/api/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    if db.query(Student).filter(Student.student_code == student.student_code).first():
        raise HTTPException(status_code=400, detail="Student code already exists")
    if db.query(Student).filter(Student.email == student.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    db_student = Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/api/students", response_model=PaginatedStudentResponse)
def list_students(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    major: Optional[str] = Query(None),
    min_gpa: Optional[float] = Query(None, ge=0.0, le=4.0),
    max_gpa: Optional[float] = Query(None, ge=0.0, le=4.0),
    db: Session = Depends(get_db)
):
    query = db.query(Student)
    if search:
        fmt = f"%{search}%"
        query = query.filter(or_(Student.full_name.like(fmt), Student.student_code.like(fmt), Student.email.like(fmt)))
    if major:
        query = query.filter(Student.major == major)
    if min_gpa is not None:
        query = query.filter(Student.gpa >= min_gpa)
    if max_gpa is not None:
        query = query.filter(Student.gpa <= max_gpa)
    
    total = query.count()
    students = query.offset((page - 1) * limit).limit(limit).all()
    return {"total": total, "page": page, "limit": limit, "data": students}

@app.get("/api/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/api/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student_data.email:
        existing = db.query(Student).filter(Student.email == student_data.email).first()
        if existing and existing.id != student_id:
            raise HTTPException(status_code=400, detail="Email already taken")

    for key, value in student_data.model_dump(exclude_unset=True).items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student

@app.delete("/api/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return None