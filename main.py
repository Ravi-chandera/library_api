from fastapi import FastAPI, HTTPException, Query, Depends
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId
from typing import List

app = FastAPI()
uri = "mongodb+srv://ravi:12345@cluster0.hpw4hsi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Initialize MongoDB client
client = MongoClient(uri)
db = client["library_databse"]
books_collection = db["books_collection"]
borrows_collection = db["borrowed_collection"]
# document = {"name of book": "hands on machine learning","author":"ravi chandera"}
# inserted_document = books_collection.insert_one(document)
# print("id of inserted document--->",inserted_document.inserted_id)
# client.close()


# Mocked user authentication function

async def fake_user_authentication(username: str, password: str):
    # You can implement your own user authentication logic here
    if username == "admin" and password == "password":
        return True
    else:
        return False

# Model for Book schema
class Book(BaseModel):
    title: str
    book_id: str
    author: str
    year: int

# Model for Borrow schema
class Borrow(BaseModel):
    user_id: str
    book_id: str
    due_date: str

# Model for Pagination
class Pagination(BaseModel):
    skip: int = Query(0, ge=0)
    limit: int = Query(10, le=100)

# API to create a new book
@app.post("/books/", response_model=Book)
async def create_book(book: Book):
    book_dict = book.dict()
    result = books_collection.insert_one(book_dict)
    return {**book_dict, "id": str(result.inserted_id)}

# API to get all books
@app.get("/books/", response_model=List[Book])
async def get_all_books(pagination: Pagination = Depends()):
    books = []
    for book in books_collection.find().skip(pagination.skip).limit(pagination.limit):
        books.append({**book, "id": str(book.pop("_id"))})
    return books

# API to search books by title or author
@app.get("/books/search/", response_model=List[Book])
async def search_books(query: str = Query(...)):
    books = []
    for book in books_collection.find({"$or": [{"title": {"$regex": query, "$options": "i"}}, {"author": {"$regex": query, "$options": "i"}}]}):
        books.append({**book, "id": str(book.pop("_id"))})
    return books

# API to get a single book by ID
@app.get("/books/{book_id}", response_model=Book)
async def get_book_by_id(book_id: str):
    book = books_collection.find_one({"_id": ObjectId(book_id)})
    if book:
        return {**book, "id": str(book.pop("_id"))}
    else:
        raise HTTPException(status_code=404, detail="Book not found")

# API to update a book by ID
@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: str, book: Book):
    book_data = book.dict()
    result = books_collection.update_one({"_id": ObjectId(book_id)}, {"$set": book_data})
    if result.modified_count == 1:
        return {**book_data, "id": book_id}
    else:
        raise HTTPException(status_code=404, detail="Book not found")

# User Authentication and Authorization
@app.post("/login/")
async def login(username: str, password: str):
    if await fake_user_authentication(username, password):
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
# Adding Categories and Tags to Books
@app.put("/books/{book_id}/categories/")
async def add_categories_to_book(book_id: str, categories: List[str]):
    result = books_collection.update_one({"_id": ObjectId(book_id)}, {"$addToSet": {"categories": {"$each": categories}}})
    if result.modified_count != 1:
        raise HTTPException(status_code=404, detail="Book not found")

@app.put("/books/{book_id}/tags/")
async def add_tags_to_book(book_id: str, tags: List[str]):
    result = books_collection.update_one({"_id": ObjectId(book_id)}, {"$addToSet": {"tags": {"$each": tags}}})
    if result.modified_count != 1:
        raise HTTPException(status_code=404, detail="Book not found")

# Tracking Borrowed Books and Due Dates
@app.post("/borrows/", response_model=Borrow)
async def borrow_book(borrow: Borrow):
    borrow_dict = borrow.dict()
    result = borrows_collection.insert_one(borrow_dict)
    return {**borrow_dict, "id": str(result.inserted_id)}

# API to delete a book by ID
@app.delete("/books/{book_id}", status_code=204)
async def delete_book(book_id: str):
    result = books_collection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count != 1:
        raise HTTPException(status_code=404, detail="Book not found")


