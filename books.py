from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional

class Book(BaseModel):
    id: int
    title: str
    author: str
    category: Optional[str] = None
    publication_year: Optional[int] = None

app = FastAPI()

books_db: List[Book] = []

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api-endpoint")
def first_api():
    return {'message': 'Hello'}

@app.get("/books")
async def read_all_books():
    return {'books': books_db}

@app.get("/books/mybook")
async def read_book():
    return {'book_title': 'MyFavoriteBook'}

@app.get("/books/{dynamic_param}")
async def read_books(dynamic_param):
    return {'dynamic_param': dynamic_param}

@app.post("/books/create_book")
async def create_book(new_book: Book):
    new_book.id = len(books_db) + 1  # Simple way to generate a unique ID
    books_db.append(new_book)
    return {"message": "Book created successfully", "book": new_book}

@app.put("/books/update_book/{book_id}")
async def update_book(book_id: int, updated_book: Book):
    for i, book in enumerate(books_db):
        if book.id == book_id:
            updated_book.id = book_id  # Ensure the updated book retains its original ID
            books_db[i] = updated_book
            return {"message": f"Book with id {book_id} has been updated", "book": updated_book}
    raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

@app.delete("/books/delete_book/{book_id}")
async def delete_book(book_id: int):
    for i, book in enumerate(books_db):
        if book.id == book_id:
            del books_db[i]
            return {"message": f"Book with id {book_id} has been deleted"}
    raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

@app.patch("/books/patch/{book_id}")
async def patch_book(book_id: int, patch_data: Book):
    stored_book_data = None
    for book in books_db:
        if book.id == book_id:
            stored_book_data = book
            update_data = patch_data.dict(exclude_unset=True)
            updated_book = stored_book_data.copy(update=update_data)
            books_db[books_db.index(book)] = updated_book
            return {"message": f"Book with id {book_id} has been patched", "book": updated_book}
    if stored_book_data is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
