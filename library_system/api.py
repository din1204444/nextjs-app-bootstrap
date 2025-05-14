from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .operations import LibrarySystem
from .config import Config

app = FastAPI(
    title=Config.LIBRARY_NAME,
    description="Library Management System API",
    version=Config.VERSION
)

library = LibrarySystem()

# Pydantic models for request/response
class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    isbn: str
    quantity: int

class UserCreate(BaseModel):
    name: str
    email: str
    student_id: Optional[str] = None
    membership_type: str

class TransactionCreate(BaseModel):
    book_id: int
    user_id: int

# API Routes
@app.get("/")
async def root():
    return library.get_system_info()

# Books endpoints
@app.post("/books/")
async def create_book(book: BookCreate):
    try:
        return library.add_book(
            title=book.title,
            author=book.author,
            genre=book.genre,
            isbn=book.isbn,
            quantity=book.quantity
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/books/")
async def list_books(search: Optional[str] = None):
    if search:
        return library.search_books(search)
    return library.session.query(library.models.Book).all()

@app.get("/books/{book_id}")
async def get_book(book_id: int):
    book = library.session.query(library.models.Book).get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Users endpoints
@app.post("/users/")
async def create_user(user: UserCreate):
    try:
        return library.add_user(
            name=user.name,
            email=user.email,
            student_id=user.student_id,
            membership_type=user.membership_type
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/")
async def list_users(search: Optional[str] = None):
    if search:
        return library.search_users(search)
    return library.session.query(library.models.User).all()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = library.session.query(library.models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/{user_id}/history")
async def get_user_history(user_id: int):
    return library.get_user_history(user_id)

# Transactions endpoints
@app.post("/transactions/borrow")
async def borrow_book(transaction: TransactionCreate):
    try:
        return library.borrow_book(
            book_id=transaction.book_id,
            user_id=transaction.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/transactions/{transaction_id}/return")
async def return_book(transaction_id: int):
    try:
        return library.return_book(transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/transactions/overdue")
async def list_overdue():
    return library.get_overdue_books()

# Cleanup
@app.on_event("shutdown")
async def shutdown_event():
    library.close()
