from fastapi import FastAPI, HTTPException, Query, Depends
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId
from typing import List

# Initialize FastAPI
app = FastAPI()

# MongoDB URI
uri = "mongodb+srv://ravi:12345@cluster0.hpw4hsi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Initialize MongoDB client
client = MongoClient(uri)
db = client["library_database"]
books_collection = db["books_collection"]
borrows_collection = db["borrowed_collection"]
print(books_collection)

# Define Pydantic models
class Book(BaseModel):
    title: str
    author: str
    genre: str

# Add a new book to the database
@app.post("/books/")
async def add_book(book: Book):
    book_dict = book.dict()
    result = books_collection.insert_one(book_dict)
    return {"message": "Book added successfully", "id": str(result.inserted_id)}

# Get a list of all available books
@app.get("/books/")
async def get_books():
    books = []
    for book in books_collection.find():
        # Convert ObjectId to string to make it JSON serializable
        book['_id'] = str(book['_id'])
        books.append(book)
        print("booksss",books)
    return books
