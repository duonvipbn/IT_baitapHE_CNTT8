from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Generator
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "mysql+pymysql://root:19112006@localhost:3306/connect_db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=False)

Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

class StudentUpdatePUT(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    age: int = Field(..., gt=0)

class StudentUpdatePATCH(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, gt=0)

@app.put("/students/{student_id}")
def update_student_full(student_id: int, payload: StudentUpdatePUT, db: Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        existing_email = db.query(Student).filter(
            Student.email == payload.email, 
            Student.id != student_id
        ).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        student.name = payload.name
        student.email = payload.email
        student.age = payload.age

        db.commit()
        db.refresh(student)
        return student

    except HTTPException as http_ex:
        raise http_ex
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")

@app.patch("/students/{student_id}")
def update_student_partial(student_id: int, payload: StudentUpdatePATCH, db: Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        update_data = payload.dict(exclude_unset=True)

        if "email" in update_data and update_data["email"] != student.email:
            existing_email = db.query(Student).filter(
                Student.email == update_data["email"], 
                Student.id != student_id
            ).first()
            if existing_email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        for key, value in update_data.items():
            setattr(student, key, value)

        db.commit()
        db.refresh(student)
        return student

    except HTTPException as http_ex:
        raise http_ex
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        db.delete(student)
        db.commit()
        return None

    except HTTPException as http_ex:
        raise http_ex
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")