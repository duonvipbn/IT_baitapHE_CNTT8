from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://root:19112006@localhost:3306/connect_db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
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

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str  
    password: str
    phone_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/students", response_model=List[StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID = {student_id}",
        )
    return student