from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.books.routes import book_router
from src.auth.routers import auth_router
from src.reviews.routes import review_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from .error import register_all_errors
from .middleware import registor_middleware


@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"Server is starting .....")
    from src.db.models import Book

    await init_db()
    yield
    print(f"Server has been stopped!!")


version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version=version,
    doc_url = f"/api/{version}/docs",
    redoc_url = f"/api/{version}/redocs",
    contact={
        "email":"abhishekpandy25@gmail.com"
    }
    # lifespan=life_span
)


register_all_errors(app)
registor_middleware(app)

@app.get("/")
async def root():
    return {"message": "API is running!"}

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
