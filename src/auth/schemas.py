from pydantic import BaseModel, Field
import uuid
from src.reviews.schema import ReviewModel
from typing import List
from src.books.schemas import Book
from datetime import datetime


# user create class
class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


# response model
class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    create_at: datetime
    update_at: datetime


class UserBooksModel(UserModel):
    books: List[Book]
    reviews: List[ReviewModel]


# for logging user
class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class EmailModel(BaseModel):
    addresses: List[str]


class PasswordRestRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
