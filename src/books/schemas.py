from pydantic import BaseModel
from datetime import date
from datetime import datetime
from src.reviews.schema import ReviewModel
from typing import List
import uuid


# Response schema
class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    create_at: datetime
    update_at: datetime


class BookDetailModel(Book):
    reviews: List[ReviewModel]


# Model create schema
class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


# Model update schmea
class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
