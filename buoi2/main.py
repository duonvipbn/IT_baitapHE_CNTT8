from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

books_db = [
    {
        "id": 1,
        "title": "Lap trinh Python Core",
        "author": "Nguyen Van A",
        "category": "IT",
        "price": 150000.0
    },
    {
        "id": 2,
        "title": "Cau truc du lieu va Giai thuat",
        "author": "Tran Van B",
        "category": "IT",
        "price": 120000.0
    },
    {
        "id": 3,
        "title": "Dac nhan tam",
        "author": "Duong Ng",
        "category": "Ky nang",
        "price": 99000.0
    }
]

class BookCreate(BaseModel):
    title: str
    author: str
    category: str
    price: float

@app.get("/books")
def get_books(category: str = ""):
    if category:
        filtered = [b for b in books_db if b["category"].lower() == category.lower()]
        return filtered
    return books_db

@app.get("/books/search")
def search_books(q: str = ""):
    query = q.lower()
    results = [
        b for b in books_db 
        if query in b["title"].lower() or query in b["author"].lower()
    ]
    return results

@app.get("/books/{book_id}")
def get_book_by_id(book_id: int):
    for book in books_db:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Khong tim thay sach!")

@app.post("/books", status_code=201)
def create_book(book_in: BookCreate):
    new_id = max([b["id"] for b in books_db], default=0) + 1
    new_book = {
        "id": new_id,
        "title": book_in.title,
        "author": book_in.author,
        "category": book_in.category,
        "price": book_in.price
    }
    books_db.append(new_book)
    return new_book

@app.put("/books/{book_id}")
def update_book_full(book_id: int, book_in: BookCreate):
    for book in books_db:
        if book["id"] == book_id:
            book["title"] = book_in.title
            book["author"] = book_in.author
            book["category"] = book_in.category
            book["price"] = book_in.price
            return book
    raise HTTPException(status_code=404, detail="Khong tim thay sach!")

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    for i, book in enumerate(books_db):
        if book["id"] == book_id:
            books_db.pop(i)
            return
    raise HTTPException(status_code=404, detail="Khong tim thay sach!")