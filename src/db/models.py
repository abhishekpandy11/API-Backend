from sqlmodel import SQLModel
from typing import List, Optional
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column, Relationship
import uuid
from datetime import datetime, date


# ================= USER MODEL =================


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )

    username: str
    email: str
    first_name: str
    last_name: str

    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )

    is_verified: bool = Field(default=False)

    password_hash: str = Field(exclude=True)

    create_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    books: List["Book"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    reviews: List["Review"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self):
        return f"<User {self.username}>"


# ================= BOOK MODEL =================


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str

    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")

    create_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    user: Optional["User"] = Relationship(back_populates="books")

    # ⭐ Missing relationship added
    reviews: List["Review"] = Relationship(
        back_populates="book",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self):
        return f"<Book {self.title}>"


# ================= REVIEW MODEL =================


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )

    rating: int = Field(lt=5)
    review_text: str

    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid")

    create_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    user: Optional["User"] = Relationship(back_populates="reviews")

    book: Optional["Book"] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for {self.book_uid} by user {self.user_uid}>"
