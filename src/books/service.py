from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from src.db.models import Book


class BookService:

    # fatcing all data
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.create_at))
        result = await session.exec(statement)
        return result.all()

    # fatch the data by user_uid
    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.create_at))
        )
        result = await session.exec(statement)
        return result.all()

    # fatcing the date
    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None

    # creating the data
    async def create_book(
        self, book_data: BookCreateModel, user_uid: str, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)

        new_book.user_uid = user_uid
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

    # updating the data
    async def update_book(
        self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.get_book(book_uid, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump(
                exclude_unset=True
            )  # Sirf wahi fields update karein jo user ne bheje hain

            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()
            await session.refresh(book_to_update)
            return book_to_update
        return None

    # deleting the data
    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)
        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return True
        return None
