from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import List
from .schemas import Book, BookUpdateModel, BookCreateModel, BookDetailModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session
from src.auth.dependencies import AcessTokenBearer, RoleChecker
from src.error import BookNotFound

book_router = APIRouter()
book_service = BookService()
acess_token_bearer = AcessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))

# --- Routes Start Here ---


# ================= GET THE DATA ===================================


@book_router.get("/", response_model=List[Book], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acess_token_bearer),
):
    # print(token_details)
    books = await book_service.get_all_books(session)
    return books


# ==========GET THE DATA BY USER UUID=======================


@book_router.get(
    "/user/{user_uid}", response_model=List[Book], dependencies=[role_checker]
)
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acess_token_bearer),
):
    # print(token_details)
    books = await book_service.get_user_books(user_uid, session)
    return books


# ================CREATE THE DATA================================


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_a_books(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acess_token_bearer),
):
    # Ab sirf database me save hoga, koi JSON file ka error nahi aayega
    user_id = token_details.get("user")["user_uid"]
    new_book = await book_service.create_book(book_data, user_id, session)
    return new_book


#
# ==============GET DATA BY ID===================================


@book_router.get(
    "/{book_uid}", response_model=BookDetailModel, dependencies=[role_checker]
)
async def get_books(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acess_token_bearer),
):
    book = await book_service.get_book(book_uid, session)
    if book:
        return book
    else:
        raise BookNotFound()


# ================UPDATE THE DATA===================================


@book_router.patch("/{book_uid}", response_model=Book, dependencies=[role_checker])
async def update_books(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acess_token_bearer),
):
    updated_book = await book_service.update_book(book_uid, book_update_data, session)

    if updated_book:
        return updated_book
    else:
        raise BookNotFound()

# ===============DELETE THE DATA===================================


@book_router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def del_books(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acess_token_bearer),
):
    book_to_delete = await book_service.delete_book(book_uid, session)

    if book_to_delete:
        return None and {
            "messge": "data deleted"
        }  # 204 No Content me kuch return nahi karte
    else:
        raise BookNotFound()
