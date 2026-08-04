from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "mysql+pymysql://root:19112006@localhost:3306/connect_db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_code = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=True)

Base.metadata.create_all(bind=engine)

class StudentBase(BaseModel):
    student_code: str
    full_name: str
    email: EmailStr
    age: Optional[int] = None

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True

app = FastAPI(title="Student Management API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    existing_code = db.query(StudentModel).filter(StudentModel.student_code == student.student_code).first()
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã sinh viên '{student.student_code}' đã tồn tại."
        )

    existing_email = db.query(StudentModel).filter(StudentModel.email == student.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{student.email}' đã tồn tại."
        )

    db_student = StudentModel(
        student_code=student.student_code,
        full_name=student.full_name,
        email=student.email,
        age=student.age
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students", response_model=List[StudentResponse])
def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(StudentModel).offset(skip).limit(limit).all()

@app.get("/students/{id}", response_model=StudentResponse)
def get_student_by_id(id: int, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.id == id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID = {id}"
        )
    return student