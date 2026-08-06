from typing import Generic, List, Optional, TypeVar
from fastapi import Depends, FastAPI, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, Column, Integer, String, create_engine, or_
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://root:19112006@localhost:3306/connect_db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

T = TypeVar("T")


class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_code = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)


Base.metadata.create_all(bind=engine)


class StudentResponse(BaseModel):
    id: int
    student_code: str
    full_name: str
    email: EmailStr
    age: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: List[StudentResponse]


app = FastAPI(title="Student Search API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/students/search",
    response_model=PaginatedResponse[StudentResponse],
    status_code=status.HTTP_200_OK,
)
def search_students(
    keyword: Optional[str] = Query(None),
    min_age: Optional[int] = Query(None, ge=0),
    max_age: Optional[int] = Query(None, ge=0),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(StudentModel)

    if keyword:
        search_pattern = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                StudentModel.full_name.ilike(search_pattern),
                StudentModel.email.ilike(search_pattern),
            )
        )

    if min_age is not None:
        query = query.filter(StudentModel.age >= min_age)

    if max_age is not None:
        query = query.filter(StudentModel.age <= max_age)

    if is_active is not None:
        query = query.filter(StudentModel.is_active == is_active)

    total = query.count()

    offset = (page - 1) * page_size
    items = (
        query.order_by(StudentModel.id.asc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }